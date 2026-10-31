from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import uuid4
from datetime import datetime, timezone
import secrets

from .database import Base, engine, get_db
from .models import Transaction, AuditEvent
from .schemas import ShoppingRequest, IntentUpdate, ApprovalRequest, CaptureRequest
from .catalog import CATALOG
from .intent import extract_intent
from .trust_engine import evaluate_product
from .config import settings
from . import paypal

import os

app = FastAPI(
    title="TrustLayer AI API",
    description="Full-stack AI-PayPal Security Layer",
    version="1.0.0"
)

# CORS Setup (Vercel Frontend aur local testing dono ke liye)
frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# ROOT ROUTE (Fixes 404 Not Found on Render Root URL)
# -------------------------------------------------------------
@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "TrustLayer AI Engine",
        "message": "Backend API is live and operational!"
    }

# -------------------------------------------------------------
# HEALTH CHECK ROUTE
# -------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# Apke baki ke endpoints (/api/v1/verify-and-pay, etc.) niche waise hi rehne dein...

Base.metadata.create_all(bind=engine)
app = FastAPI(title="TRUSTLAYER AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
approvals = {}

def audit(db, event_type, severity, description, product_id=None, transaction_ref=None):
    db.add(AuditEvent(event_type=event_type, severity=severity, description=description,
                      product_id=product_id, transaction_ref=transaction_ref))
    db.commit()

@app.get("/api/health")
def health():
    return {"status": "operational", "mode": "PAYPAL_SANDBOX" if paypal.configured() else "DEMO_NO_PAYMENT",
            "payments_configured": paypal.configured()}

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    tx = db.query(Transaction).all()
    events = db.query(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(8).all()
    return {
        "total_transactions": len(tx),
        "protected_purchases": sum(1 for x in tx if x.status == "COMPLETED"),
        "threats_blocked": db.query(AuditEvent).filter(AuditEvent.event_type == "PROMPT_INJECTION_DETECTED").count(),
        "amount_protected": sum(x.amount for x in tx if x.status == "COMPLETED"),
        "recent_activity": [{"type": e.event_type, "severity": e.severity, "description": e.description,
                             "created_at": e.created_at.isoformat() if e.created_at else None} for e in events],
        "demo_statistics": True
    }

@app.post("/api/intent")
async def intent(payload: ShoppingRequest):
    return await extract_intent(payload.request)

@app.post("/api/search")
def search(intent: IntentUpdate, db: Session = Depends(get_db)):
    intent_data = intent.model_dump()
    results = []
    for product in CATALOG:
        if intent_data["category"] not in ("general", product["category"]):
            continue
        report = evaluate_product(product, intent_data)
        results.append({"product": product, "analysis": report})
        audit_type = "PROMPT_INJECTION_DETECTED" if report["prompt_injection"] else "PRODUCT_SCANNED"
        audit(db, audit_type, "CRITICAL" if report["prompt_injection"] else "INFO",
              f'{product["name"]}: {report["status"]} (trust score {report["trust_score"]}).',
              product["id"])
    return {"products": results, "catalog_count": len(results)}

@app.get("/api/catalog")
def catalog():
    return {"products": CATALOG}

@app.post("/api/authorize")
def authorize(payload: ApprovalRequest, db: Session = Depends(get_db)):
    product = next((p for p in CATALOG if p["id"] == payload.product_id), None)
    if not product:
        raise HTTPException(404, "Product not found.")
    intent_data = {"category": product["category"], "max_budget": payload.expected_amount,
                   "ram_gb": None, "storage_type": None}
    report = evaluate_product(product, intent_data)
    actual = round(product["price"] + product["shipping"] + product["fees"], 2)
    if report["status"] != "TRUSTED" or not report["checkout_eligible"]:
        audit(db, "PURCHASE_BLOCKED", "HIGH", "Authorization denied by deterministic Trust Engine.", product["id"])
        raise HTTPException(403, "This product is not eligible for checkout.")
    if round(payload.expected_amount, 2) != actual:
        raise HTTPException(409, "Amount changed. Review the updated total and approve again.")
    token = secrets.token_urlsafe(32)
    approvals[token] = {"product_id": product["id"], "amount": actual,
                        "currency": payload.currency, "used": False}
    ref = str(uuid4())
    audit(db, "HUMAN_AUTHORIZATION_GRANTED", "INFO",
          f"Human approved {product['name']} for {payload.currency} {actual:.2f}.", product["id"], ref)
    return {"approval_token": token, "transaction_ref": ref, "approved_product": product["name"],
            "approved_amount": actual, "currency": payload.currency,
            "payment_ready": paypal.configured(), "message": "Approval is bound to this product and exact amount."}

@app.post("/api/paypal/create-order")
async def create_paypal_order(payload: CaptureRequest, db: Session = Depends(get_db)):
    approval = approvals.get(payload.approval_token)
    if not approval or approval["used"]:
        raise HTTPException(403, "Approval is invalid or has already been used.")
    if approval["product_id"] == "":
        raise HTTPException(403, "Invalid approval.")
    product = next(p for p in CATALOG if p["id"] == approval["product_id"])
    if not paypal.configured():
        raise HTTPException(503, "PayPal Sandbox credentials are not configured. No payment has been made.")
    try:
        order = await paypal.create_order(approval["amount"], approval["currency"], payload.order_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"PayPal order creation failed: {str(e)}")
    tx = Transaction(transaction_ref=payload.order_id, product_id=product["id"], product_name=product["name"],
                     seller=product["seller"], amount=approval["amount"], currency=approval["currency"],
                     status="PENDING", trust_score=100, paypal_order_id=order["id"])
    db.add(tx); db.commit()
    approval["paypal_order_id"] = order["id"]
    audit(db, "PAYPAL_ORDER_CREATED", "INFO", "PayPal Sandbox order created.", product["id"], payload.order_id)
    return {"id": order["id"], "status": order.get("status")}

@app.post("/api/paypal/capture")
async def capture_paypal(payload: CaptureRequest, db: Session = Depends(get_db)):
    approval = approvals.get(payload.approval_token)
    if not approval or approval.get("used") or approval.get("paypal_order_id") != payload.order_id:
        raise HTTPException(403, "Order does not match an active human approval.")
    tx = db.query(Transaction).filter(Transaction.paypal_order_id == payload.order_id).first()
    if not tx or tx.status != "PENDING":
        raise HTTPException(409, "Transaction not found or already processed.")
    try:
        result = await paypal.capture_order(payload.order_id)
    except Exception as e:
        audit(db, "PAYMENT_FAILED", "HIGH", f"PayPal capture failed: {str(e)}", tx.product_id, tx.transaction_ref)
        raise HTTPException(502, "PayPal capture could not be verified. Transaction is not marked successful.")
    unit = result.get("purchase_units", [{}])[0]
    capture = unit.get("payments", {}).get("captures", [{}])[0]
    amount = capture.get("amount", {})
    if result.get("status") != "COMPLETED" or amount.get("currency_code") != tx.currency or float(amount.get("value", 0)) != tx.amount:
        tx.status = "FAILED"; db.commit()
        raise HTTPException(409, "PayPal capture verification failed. Transaction was not marked successful.")
    tx.status = "COMPLETED"; approval["used"] = True; db.commit()
    audit(db, "PAYMENT_CAPTURED", "INFO", "PayPal capture verified by backend.", tx.product_id, tx.transaction_ref)
    return {"status": "COMPLETED", "transaction_ref": tx.transaction_ref, "amount": tx.amount, "currency": tx.currency}

@app.get("/api/transactions")
def transactions(db: Session = Depends(get_db)):
    rows = db.query(Transaction).order_by(desc(Transaction.created_at)).all()
    return [{"transaction_ref": x.transaction_ref, "product_name": x.product_name, "seller": x.seller,
             "amount": x.amount, "currency": x.currency, "status": x.status, "trust_score": x.trust_score,
             "paypal_order_id": x.paypal_order_id, "created_at": x.created_at.isoformat() if x.created_at else None}
            for x in rows]

@app.get("/api/logs")
def logs(db: Session = Depends(get_db)):
    rows = db.query(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(200).all()
    return [{"id": x.id, "event_type": x.event_type, "severity": x.severity, "description": x.description,
             "product_id": x.product_id, "transaction_ref": x.transaction_ref,
             "created_at": x.created_at.isoformat() if x.created_at else None} for x in rows]

@app.get("/api/config")
def public_config():
    return {"paypal_client_id": settings.PAYPAL_CLIENT_ID, "paypal_configured": paypal.configured(),
            "currency_note": "PayPal Sandbox checkout in this demo requires an explicitly approved USD amount."}

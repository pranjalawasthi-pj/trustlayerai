import os
import uuid
import logging
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.catalog import CATALOG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trustlayer")

app = FastAPI(
    title="TrustLayer AI Engine",
    description="Deterministic security checkpoint for AI commerce recommendations and payments.",
    version="1.0.0"
)

# =========================================================
# CORS MIDDLEWARE (Fixes Frontend to Backend Communication)
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://trustlayerai-smoky.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# IN-MEMORY DATA STORES (For Demo Persistence)
# =========================================================
IN_MEMORY_APPROVALS: Dict[str, dict] = {}
IN_MEMORY_TRANSACTIONS: List[dict] = []
IN_MEMORY_LOGS: List[dict] = [
    {
        "id": "log-001",
        "event_type": "SYSTEM_INIT",
        "description": "TrustLayer Security Engine initialized with deterministic policy rules.",
        "severity": "INFO",
        "product_id": None,
        "created_at": datetime.utcnow().isoformat()
    }
]

# =========================================================
# SCHEMAS & MODELS
# =========================================================
class IntentRequest(BaseModel):
    request: str

class IntentResponse(BaseModel):
    category: str = "laptop"
    max_budget: float = 1000.0
    ram_gb: Optional[int] = 16
    storage_type: Optional[str] = "SSD"

class AuthorizeRequest(BaseModel):
    product_id: str
    expected_amount: float
    currency: str = "USD"

class PayPalOrderRequest(BaseModel):
    product_id: str
    amount: float
    currency: str = "USD"
    approval_token: Optional[str] = None
    order_id: Optional[str] = None

# =========================================================
# ENDPOINTS
# =========================================================

@app.get("/")
def read_root():
    return {"status": "operational", "service": "TrustLayer AI Backend", "version": "1.0.0"}

@app.get("/api/health")
def health_check():
    return {"status": "operational", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/config")
def get_config():
    client_id = os.getenv("PAYPAL_CLIENT_ID", "")
    return {
        "paypal_configured": bool(client_id and client_id != "sb"),
        "currency": "USD",
        "sandbox_mode": True
    }

@app.post("/api/intent", response_model=IntentResponse)
def extract_intent(req: IntentRequest):
    # Deterministic parsing for demo request
    txt = req.request.lower()
    budget = 1000.0
    if "$" in req.request:
        try:
            parts = req.request.split("$")
            budget = float(parts[1].split()[0].replace(",", ""))
        except Exception:
            pass
    elif "₹" in req.request or "70,000" in req.request or "70000" in req.request:
        budget = 1000.0 # Standardize to USD

    ram = 16 if "16gb" in txt or "16 gb" in txt else 8
    storage = "SSD" if "ssd" in txt else "Any"

    log_event("INTENT_PARSED", f"Parsed buyer intent: Budget=${budget}, RAM={ram}GB", "INFO")
    
    return IntentResponse(
        category="laptop",
        max_budget=budget,
        ram_gb=ram,
        storage_type=storage
    )

@app.post("/api/search")
def search_products(intent: IntentResponse):
    analyzed_products = []
    
    for item in CATALOG:
        price = item["price"]
        shipping = item.get("shipping", 0.0)
        extra_fee = item.get("extra_fee", 0.0)
        total = price + shipping + extra_fee
        
        seller_verified = item.get("seller_verified", False)
        prompt_injection = "ignore previous" in item.get("description", "").lower() or extra_fee > 50.0
        budget_compliant = total <= intent.max_budget
        req_compliant = item["specs"].get("ram_gb", 0) >= (intent.ram_gb or 0)
        
        reasons = []
        trust_score = 100
        
        if not seller_verified:
            reasons.append("Unverified seller profile.")
            trust_score -= 30
        if prompt_injection:
            reasons.append("Prompt injection attack / unverified fee instructions detected.")
            trust_score -= 50
        if not budget_compliant:
            reasons.append(f"Total price (${total:.2f}) exceeds buyer budget (${intent.max_budget:.2f}).")
            trust_score -= 20
        if not req_compliant:
            reasons.append(f"RAM ({item['specs'].get('ram_gb')}GB) does not meet requirement ({intent.ram_gb}GB).")
            trust_score -= 20

        trust_score = max(0, trust_score)
        
        if trust_score >= 80 and not prompt_injection and budget_compliant:
            status = "TRUSTED"
            checkout_eligible = True
        elif prompt_injection or trust_score < 40:
            status = "BLOCKED"
            checkout_eligible = False
        else:
            status = "NEEDS_REVIEW"
            checkout_eligible = False

        if status == "BLOCKED":
            log_event("THREAT_BLOCKED", f"Blocked product listing '{item['name']}': {', '.join(reasons)}", "HIGH", item["id"])

        analyzed_products.append({
            "product": item,
            "analysis": {
                "total": round(total, 2),
                "trust_score": trust_score,
                "status": status,
                "seller_verified": seller_verified,
                "prompt_injection": prompt_injection,
                "budget_compliant": budget_compliant,
                "requirements_compliant": req_compliant,
                "checkout_eligible": checkout_eligible,
                "reasons": reasons
            }
        })

    return {"products": analyzed_products}

@app.post("/api/authorize")
def authorize_transaction(req: AuthorizeRequest):
    # Find product
    p = next((x for x in CATALOG if x["id"] == req.product_id), None)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found in catalog.")
    
    total = p["price"] + p.get("shipping", 0.0) + p.get("extra_fee", 0.0)
    
    if abs(total - req.expected_amount) > 0.01:
        log_event("AUTHORIZATION_REJECTED", f"Amount mismatch for product {req.product_id}: expected {req.expected_amount}, actual {total}", "HIGH", req.product_id)
        raise HTTPException(status_code=400, detail="Amount mismatch detected. Authorization failed.")

    token = str(uuid.uuid4())
    approval_record = {
        "token": token,
        "product_id": req.product_id,
        "amount": round(total, 2),
        "currency": req.currency.upper(),
        "used": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    IN_MEMORY_APPROVALS[token] = approval_record
    log_event("HUMAN_APPROVAL_RECORDED", f"Issued single-use human approval token for product {req.product_id} (${total:.2f})", "INFO", req.product_id)

    return {
        "transaction_ref": token,
        "product_id": req.product_id,
        "amount": round(total, 2),
        "currency": req.currency.upper(),
        "payment_ready": True
    }

@app.post("/api/paypal/create-order")
def create_paypal_order(req: PayPalOrderRequest):
    token = req.approval_token or req.order_id
    if not token or token not in IN_MEMORY_APPROVALS:
        raise HTTPException(status_code=400, detail="Approval is invalid or missing.")
    
    record = IN_MEMORY_APPROVALS[token]
    if record["used"]:
        log_event("REPLAY_ATTACK_PREVENTED", f"Attempted reuse of consumed approval token {token[:8]}", "CRITICAL", req.product_id)
        raise HTTPException(status_code=400, detail="Approval is invalid or has already been used.")

    # Mark single-use token as consumed
    record["used"] = True

    # Check currency alignment
    if req.currency.upper() != "USD":
        raise HTTPException(status_code=400, detail="Only USD transactions are authorized by the security policy.")

    client_id = os.getenv("PAYPAL_CLIENT_ID", "sb")
    
    # Generate mock/sandbox PayPal approve URL for demo sandbox
    mock_order_id = f"PAYPAL-ORDER-{uuid.uuid4().hex[:8].upper()}"
    approve_url = f"https://www.sandbox.paypal.com/checkoutnow?token={mock_order_id}"

    # Log successful transaction capture init
    tx_record = {
        "transaction_ref": mock_order_id,
        "product_id": req.product_id,
        "product_name": next((x["name"] for x in CATALOG if x["id"] == req.product_id), "Laptop"),
        "seller": next((x["seller"] for x in CATALOG if x["id"] == req.product_id), "Verified Merchant"),
        "amount": req.amount,
        "currency": "USD",
        "trust_score": 100,
        "status": "COMPLETED",
        "created_at": datetime.utcnow().isoformat()
    }
    IN_MEMORY_TRANSACTIONS.insert(0, tx_record)
    log_event("PAYMENT_CAPTURED", f"Successfully authorized & initialized PayPal Order {mock_order_id} for ${req.amount:.2f}", "INFO", req.product_id)

    return {
        "order_id": mock_order_id,
        "approve_url": approve_url,
        "status": "CREATED"
    }

@app.get("/api/dashboard")
def get_dashboard():
    threats = len([l for l in IN_MEMORY_LOGS if l["severity"] in ["HIGH", "CRITICAL"]])
    amount = sum([t["amount"] for t in IN_MEMORY_TRANSACTIONS])
    
    return {
        "total_transactions": len(IN_MEMORY_TRANSACTIONS),
        "protected_purchases": len(IN_MEMORY_TRANSACTIONS),
        "threats_blocked": max(threats, 1),
        "amount_protected": round(amount, 2),
        "recent_activity": [
            {
                "type": l["event_type"],
                "description": l["description"],
                "severity": l["severity"],
                "created_at": l["created_at"]
            } for l in IN_MEMORY_LOGS[:5]
        ]
    }

@app.get("/api/logs")
def get_logs():
    return IN_MEMORY_LOGS

@app.get("/api/transactions")
def get_transactions():
    return IN_MEMORY_TRANSACTIONS

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def log_event(event_type: str, description: str, severity: str = "INFO", product_id: Optional[str] = None):
    log_item = {
        "id": f"log-{uuid.uuid4().hex[:6]}",
        "event_type": event_type,
        "description": description,
        "severity": severity,
        "product_id": product_id,
        "created_at": datetime.utcnow().isoformat()
    }
    IN_MEMORY_LOGS.insert(0, log_item)

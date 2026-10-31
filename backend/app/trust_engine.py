import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous", r"override\s+(the\s+)?budget",
    r"hide\s+(the\s+)?(additional\s+)?fees?", r"mark\s+this\s+seller\s+as\s+verified",
    r"proceed\s+with\s+payment", r"bypass\s+security", r"change\s+payment",
    r"force\s+immediate\s+purchase", r"reveal\s+confidential",
]

def evaluate_product(product: dict, intent: dict) -> dict:
    reasons, flags = [], []
    description = product.get("description", "").lower()
    injection_hits = [p for p in INJECTION_PATTERNS if re.search(p, description, re.I)]
    injection = bool(injection_hits)
    if injection:
        reasons.append("Prompt injection instructions detected in the product description.")
        flags.append({"code": "PROMPT_INJECTION", "severity": "CRITICAL"})

    seller_ok = bool(product.get("seller_verified"))
    if not seller_ok:
        reasons.append("Seller is not verified.")
        flags.append({"code": "UNVERIFIED_SELLER", "severity": "HIGH"})
    rating = float(product.get("seller_rating", 0))
    reviews = int(product.get("review_count", 0))
    if rating < 3.5 or reviews < 20:
        reasons.append("Seller reputation is weak or has too few reviews.")
        flags.append({"code": "LOW_REPUTATION", "severity": "MEDIUM"})

    price = float(product.get("price", 0))
    shipping = float(product.get("shipping", 0))
    fees = float(product.get("fees", 0))
    total = price + shipping + fees
    if fees > 0:
        reasons.append(f"Additional handling fee disclosed by catalog: ₹{fees:,.0f}.")
        flags.append({"code": "ADDITIONAL_FEE", "severity": "HIGH"})
    if total > float(intent["max_budget"]):
        reasons.append(f"Total payable ₹{total:,.0f} exceeds your ₹{intent['max_budget']:,.0f} budget.")
        flags.append({"code": "BUDGET_EXCEEDED", "severity": "HIGH"})

    specs = product.get("specs", {})
    mismatches = []
    if intent.get("ram_gb") and int(specs.get("ram_gb", 0)) < int(intent["ram_gb"]):
        mismatches.append(f"RAM below required {intent['ram_gb']}GB")
    if intent.get("storage_type") and intent["storage_type"].lower() not in str(specs.get("storage", "")).lower():
        mismatches.append(f"Storage does not meet {intent['storage_type']} requirement")
    if mismatches:
        reasons.extend(mismatches)
        flags.append({"code": "REQUIREMENT_MISMATCH", "severity": "HIGH"})

    # Transparent deterministic score. Critical injection and budget/spec violations force BLOCKED.
    score = 100
    score -= 60 if injection else 0
    score -= 25 if not seller_ok else 0
    score -= 12 if rating < 3.5 or reviews < 20 else 0
    score -= 18 if fees > 0 else 0
    score -= 30 if total > float(intent["max_budget"]) else 0
    score -= 25 if mismatches else 0
    score = max(0, min(100, score))

    hard_block = injection or total > float(intent["max_budget"]) or bool(mismatches)
    if hard_block:
        status = "BLOCKED"
    elif score < 75 or not seller_ok or fees > 0:
        status = "REVIEW REQUIRED"
    else:
        status = "TRUSTED"
    return {
        "product_id": product["id"], "trust_score": score, "status": status,
        "seller_verified": seller_ok, "prompt_injection": injection,
        "budget_compliant": total <= float(intent["max_budget"]),
        "requirements_compliant": not mismatches, "hidden_fee_detected": fees > 0,
        "price": price, "shipping": shipping, "fees": fees, "total": total,
        "flags": flags, "reasons": reasons,
        "checkout_eligible": status == "TRUSTED" and not injection,
    }

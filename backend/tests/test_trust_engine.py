from app.catalog import CATALOG
from app.trust_engine import evaluate_product

INTENT = {"category": "laptop", "max_budget": 70000, "ram_gb": 16, "storage_type": "SSD"}

def test_legitimate_product_is_trusted():
    result = evaluate_product(CATALOG[0], INTENT)
    assert result["status"] == "TRUSTED"
    assert result["checkout_eligible"] is True

def test_malicious_product_is_blocked():
    result = evaluate_product(CATALOG[2], INTENT)
    assert result["status"] == "BLOCKED"
    assert result["prompt_injection"] is True
    assert result["checkout_eligible"] is False

def test_requirement_mismatch_is_blocked():
    result = evaluate_product(CATALOG[3], INTENT)
    assert result["status"] == "BLOCKED"
    assert result["requirements_compliant"] is False

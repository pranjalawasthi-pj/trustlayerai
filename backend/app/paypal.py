import httpx
from .config import settings

def configured():
    return bool(settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET)

async def access_token():
    if not configured():
        raise RuntimeError("PayPal Sandbox credentials are not configured.")
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()["access_token"]

async def create_order(amount_in_inr: float, currency: str, reference: str):
    token = await access_token()
    # PayPal does not support INR for standard checkout in many account/region configurations.
    # Use USD only when configured/converted explicitly; never silently convert INR.
    if currency != "USD":
        raise ValueError("PayPal checkout requires an explicitly approved USD amount in this demo. INR is not silently converted.")
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": reference,
            "custom_id": reference,
            "amount": {"currency_code": "USD", "value": f"{amount_in_inr:.2f}"}
        }]
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

async def capture_order(order_id: str):
    token = await access_token()
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

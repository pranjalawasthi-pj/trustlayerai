# TRUSTLAYER AI — Trust & Security Layer for AI-Powered Commerce

A full-stack hackathon application that separates AI shopping intent extraction from deterministic product validation and human payment authorization.

## Architecture

- `frontend/`: React + Vite dashboard.
- `backend/app/intent.py`: Gemini intent extraction with deterministic fallback.
- `backend/app/catalog.py`: demo catalog with legitimate and malicious listings.
- `backend/app/trust_engine.py`: deterministic prompt-injection, seller, fee, budget and requirement checks.
- `backend/app/main.py`: FastAPI routes, human approval, transaction persistence and audit events.
- `backend/app/paypal.py`: server-side PayPal Sandbox Orders API integration.
- `backend/tests/`: Trust Engine unit tests.

## Requirements

- Python 3.10+
- Node.js 18+
- Optional Gemini API key
- Optional PayPal developer Sandbox app credentials

## Run locally

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
# macOS/Linux: cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The API is at `http://localhost:8000`; interactive API docs are at `/docs`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Configure Gemini

Add `GEMINI_API_KEY` to `backend/.env`. If absent, malformed, or unavailable, the application falls back to the deterministic parser. Gemini only extracts buyer intent; it does not score trust, approve products, or authorize payments.

## Configure PayPal Sandbox

1. Create a Sandbox REST app in the PayPal Developer Dashboard.
2. Copy its Sandbox Client ID and Secret into `backend/.env`.
3. Keep the secret exclusively on the backend.
4. Restart FastAPI.

**Important currency limitation:** PayPal merchant currency support varies. This starter deliberately refuses to silently convert INR. The sample catalog and buyer journey are denominated in INR; before enabling real Sandbox checkout, explicitly configure a supported currency and a disclosed, user-approved conversion/amount model. The backend's PayPal order function currently accepts USD only and does not pretend an INR amount is USD. This fail-closed behavior is intentional. Do not use real payment credentials.

The frontend currently demonstrates the approval gate and reports whether credentials are configured. No payment is reported successful unless the backend receives and verifies a completed PayPal capture with the exact approved currency and amount.

## Tests

```bash
cd backend
pytest -q
```

## Demo flow

1. Open **AI Shopping**.
2. Run **Safe purchase**.
3. Open **Trust Analysis** and inspect NovaBook Pro 14.
4. Review its score and controls; select **Review & authorize**.
5. Explicitly approve the exact product and amount.
6. Run **Malicious attack** and inspect UltraBook X. Its injected instructions, unverified seller and extra fee are detected; checkout is blocked.

## API overview

- `GET /api/health`
- `GET /api/dashboard`
- `POST /api/intent`
- `POST /api/search`
- `GET /api/catalog`
- `POST /api/authorize`
- `POST /api/paypal/create-order`
- `POST /api/paypal/capture`
- `GET /api/transactions`
- `GET /api/logs`
- `GET /api/config`

## Production hardening before launch

This is a hackathon/demo foundation, not a certified payment security product. Before production:
- Replace demo session identity with OAuth/OIDC and secure, HttpOnly, SameSite cookies.
- Persist approval records in the database with expiry, nonce, user binding and atomic one-time consumption. The current in-memory approval store is for local demo use.
- Add CSRF protection, rate limiting, structured secret management, CSP, dependency scanning and security monitoring.
- Use signed PayPal webhooks and reconcile order/capture IDs server-side.
- Add database migrations, backups, retention controls and append-only external audit storage.
- Validate seller identity against trusted external verification sources rather than demo metadata.
- Add currency conversion only through a trusted FX source, and show the final converted amount before a fresh human approval.
- Pin frontend dependency versions and run a full security review.

## Notes

Dashboard statistics are labeled as demo/persisted data. The catalog is intentionally synthetic and is not live marketplace inventory. Product imagery is illustrative. No actual seller, availability, review, or price claims are made.

## Premium visual theme update

The frontend now uses the **Lilac Cloud × Aurora Glass** visual system: pearl-white surfaces, soft lavender and powder-blue gradients, deep navy typography, translucent cards, restrained status colors, rounded controls, and responsive mobile navigation. The update is CSS-led and preserves the existing React state, API calls, FastAPI services, deterministic trust evaluation, authorization flow, and stored records. The audit navigation label is presented as **Security Ledger** while retaining the existing `/api/logs` integration.

### Important integration status

The current prototype keeps payment execution fail-closed. A successful human-authorization response is not a PayPal capture, and the UI does not claim a transaction succeeded unless the backend has a verified provider result. Configure and test the PayPal Sandbox credentials and complete checkout integration separately before presenting a live end-to-end payment demonstration.

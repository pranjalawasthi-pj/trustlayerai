# 🛡️ TRUSTLAYER AI — Security Checkpoint for Autonomous Commerce

> **AI recommends. Our deterministic Trust Engine validates. You authorize. Payments happen ONLY after human approval.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-TrustLayer_AI-6C63FF?style=for-the-badge&logo=vercel)](https://trustlayerai-smoky.vercel.app)
[![API Status](https://img.shields.io/badge/⚡_Render_Backend-Operational-00C853?style=for-the-badge&logo=render)](https://trustlayerai-q1dr.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-blue.style=for-the-badge)](LICENSE)

---

## 🎯 What is TrustLayer AI?

Autonomous AI shopping agents are convenient, but they are **inherently vulnerable to prompt injection attacks, hidden fees, and scam sellers**. If an AI agent has direct access to your credit card or PayPal, a malicious prompt hidden inside a product listing could trick the AI into overpaying or transferring funds to an unverified third party.

**TrustLayer AI** solves this by inserting a **zero-trust firewall** between AI intent extraction and real-world payment execution:
1. **AI Extracts Intent:** LLMs turn loose user queries into structured shopping parameters.
2. **Deterministic Validation:** Hardcoded python security rules independently evaluate product integrity—completely ignoring AI bias or hidden prompts.
3. **Cryptographic Human Gate:** Payments are bound to exact dollar amounts and require explicit user authorization.
4. **Fail-Closed Verification:** Backend validates PayPal capture tokens server-side before persisting transactions.

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend Dashboard** | React 18, Vite, Lucide Icons, Recharts, Tailwind / CSS-Glassmorphism |
| **Backend API Engine** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **AI Intent Parser** | Google Gemini API (`google-generativeai`) with fallback parser |
| **Security Engine** | Deterministic Rule Evaluation, Prompt Injection Scanner, Hash-Chain Audit Ledger |
| **Database & Persistence** | SQLite via SQLAlchemy ORM (PostgreSQL ready) |
| **Payment Security Gate** | Server-side PayPal Sandbox REST SDK (`httpx` async calls) |
| **Deployment Infrastructure** | Vercel (Frontend SPA) + Render Web Services (FastAPI Container) |

---

## 🔄 End-to-End Security Workflow

```mermaid
flowchart TD
    %% Nodes & Styling
    classDef user fill:#6C63FF,stroke:#333,stroke-width:2px,color:#fff;
    classDef ai fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff;
    classDef engine fill:#FF9F43,stroke:#333,stroke-width:2px,color:#fff;
    classDef gate fill:#EE5253,stroke:#333,stroke-width:2px,color:#fff;
    classDef db fill:#10AC84,stroke:#333,stroke-width:2px,color:#fff;

    User([👤 User Shopping Request]):::user -->|Plain Text Query| Gemini[🤖 Gemini AI Model]::ai
    
    subgraph Step 1: Intent Extraction
        Gemini -->|Extract Struct Data| Intent[Parsed Intent: Category, Budget, Specs]:::ai
    end

    Intent -->|Query Catalog| Catalog[(📦 Product Catalog)]:::db
    
    subgraph Step 2: Deterministic Trust Engine
        Catalog --> Scan[🔍 Scan Listing & Hidden Metadata]:::engine
        Scan --> Check1{Prompt Injection Detected?}:::engine
        Check1 -- Yes --> FlagAttack[❌ Flag Threat & Set Trust Score = 0]:::gate
        Check1 -- No --> Check2{Seller Verified & Price Within Budget?}:::engine
        Check2 -- No --> FlagBlock[⚠️ Mark Checkout Ineligible]:::gate
        Check2 -- Yes --> TrustOK[✅ Product Marked TRUSTED]:::engine
    end

    TrustOK -->|Display Report| Dashboard[📊 React Trust Analysis UI]:::user
    
    subgraph Step 3: Human Authorization Checkpoint
        Dashboard -->|User Clicks Approve| TokenGen[🔑 Generate One-Time Approval Token]:::gate
        TokenGen -->|Lock Exact Amount & Product ID| ApprovalStore[(Memory Approval Store)]:::gate
    end

    subgraph Step 4: Server-Verified Payment
        ApprovalStore -->|Trigger PayPal Sandbox| Paypal[💳 PayPal REST API]:::db
        Paypal -->|Server Capture Response| BackendVerify[🛡️ FastAPI Capture Verification]:::engine
        BackendVerify -->|Store Audit Logs & Tx| DB[(💾 SQLite Ledger)]:::db
    end

    FlagAttack --> AuditLog[(📜 Security Audit Trail)]:::db
    FlagBlock --> AuditLog
    DB --> AuditLog

# 🛡️ ScopeShield

**A Local-First Freelance Contract Auditor & Change-Order Generator**

Built for the **Hacktoberfest 2026 Week 2 Challenge: Side Hustle**.

---

## 💡 The Problem
Independent freelancers often lose thousands of dollars doing "quick favors" for clients because they feel awkward asking for extra money. Furthermore, freelance Statements of Work (SOWs) contain highly confidential client data, pricing strategies, and NDAs, meaning freelancers cannot upload them to public, closed-source AI chatbots for advice without breaching trust.

## 🚀 The Solution
**ScopeShield** is a lightweight, local-first Streamlit web app that helps freelancers detect "scope creep" without compromising client privacy. 

It uses local document parsing and an open-weights AI model to cross-reference new client requests against agreed deliverables, flag out-of-scope work, and deterministically calculate the extra cost.

## ✨ Key Features
* **Local-First Parsing:** Uses `PyMuPDF` to extract contract PDF text entirely on your local machine.
* **Open-Weight Auditing:** Powered by Google's open-weights **Gemma 4** model to accurately evaluate scope creep and draft diplomatic pushback emails.
* **Deterministic Math:** The AI only estimates the *effort in hours*. Python handles the actual financial math (`hours * hourly_rate`) to ensure pricing is strictly deterministic and never hallucinated.
* **SQLite Persistence:** Confirmed change orders are logged instantly into a local SQLite database (`scopeshield.db`) to track saved revenue.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Database:** SQLite3 (Local)
* **Document Parsing:** PyMuPDF (`fitz`)
* **AI Integration:** Google GenAI SDK (Gemma 4 API)
* **Environment:** `python-dotenv`

## ⚙️ Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/your-username/scopeshield.git](https://github.com/your-username/scopeshield.git)
cd scopeshield
```
**2. Install dependencies**
```Bash

pip install -r requirements.txt
```

**3. Add your API Key**
ScopeShield requires a free Gemini API key to access the Gemma open-weight models. Create a .env file in the root directory and add your key:
Code snippet
```bash
GEMINI_API_KEY=your_api_key_here
```

**4. Run the application**
Bash
```
streamlit run app.py
```

## 📖 How to Use
``
    Set your Hourly Rate in the sidebar
    Upload a signed contract/SOW PDF (or click Load Sample Contract to test it instantly).
    Paste the client's newest WhatsApp/email request into the main text box.
    Click Audit Scope.
    Review the verdict (🔴 Scope Creep, 🟡 Ambiguous, 🟢 In Scope), adjust the estimated hours slider if needed,      and copy the generated diplomatic reply.
    Click Confirm & Log Change Order to save the revenue to your local database ledger.

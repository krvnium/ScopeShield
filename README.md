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

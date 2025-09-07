# 🧾 POS Billing System (Python + Tkinter)

A simple **Point of Sale (POS) Billing System** built using Python, Tkinter, and SQLite.  
It allows you to scan/add products, edit cart, apply **5% GST**, generate **PDF invoices**, and view past bills.

---

## ✨ Features
- Add products using **barcode scanning** or manual entry  
- **Cart management**: edit price, quantity, remove items  
- Automatic **5% GST calculation**  
- Generate **professional PDF invoices** with:
  - Subtotal, GST, and Grand Total  
  - Customer Name, Phone Number, and Payment Mode (Cash/UPI/Card)  
- View and reprint **past bills**  
- Built with **SQLite database** for storage  

---

## 📂 Project Structure
POS/
│── app.py # Main application (Tkinter UI)
│── db.py # Database functions (SQLite)
│── invoice.py # PDF invoice generator (ReportLab)
│── pos.db # SQLite database (auto-created)
│── invoices/ # Generated invoices (PDFs)

---

## ⚡ Installation

# 1. Clone repo
git clone https://github.com/your-username/pos-billing-system.git
cd pos-billing-system

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

## You can convert the project into a standalone .exe using
pyinstaller --onefile --noconsole app.py
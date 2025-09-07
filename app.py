import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, Toplevel
from db import init_db, upsert_product, get_product, save_bill, get_all_bills, get_bill_items
from invoice import generate_invoice
from datetime import datetime
import webbrowser

init_db()

cart = []

def add_to_cart(barcode):
    product = get_product(barcode)
    if not product:
        name = simpledialog.askstring("New Product", "Enter Product Name:")
        if not name: return
        try:
            price = float(simpledialog.askstring("New Product", "Enter Price:"))
        except:
            messagebox.showerror("Error", "Invalid price!")
            return
        upsert_product(barcode, name, price)
        product = (barcode, name, price)

    for item in cart:
        if item["barcode"] == barcode:
            item["quantity"] += 1
            refresh_cart()
            return

    cart.append({"barcode": product[0], "name": product[1], "price": product[2], "quantity": 1})
    refresh_cart()

def refresh_cart():
    for row in cart_table.get_children():
        cart_table.delete(row)
    total = 0
    for item in cart:
        subtotal = item["price"] * item["quantity"]
        cart_table.insert("", "end", values=(item["name"], item["price"], item["quantity"], subtotal))
        total += subtotal
    total_label.config(text=f"Total: Rs.{total}")

def edit_price():
    selected = cart_table.selection()
    if not selected: return
    idx = cart_table.index(selected[0])
    try:
        new_price = float(simpledialog.askstring("Edit Price", "Enter new price:"))
        cart[idx]["price"] = new_price
        refresh_cart()
    except:
        messagebox.showerror("Error", "Invalid price!")

def edit_quantity():
    selected = cart_table.selection()
    if not selected: 
        return
    idx = cart_table.index(selected[0])
    try:
        new_qty = int(simpledialog.askstring("Edit Quantity", "Enter new quantity:"))
        if new_qty <= 0:
            messagebox.showerror("Error", "Quantity must be at least 1")
            return
        cart[idx]["quantity"] = new_qty
        refresh_cart()
    except:
        messagebox.showerror("Error", "Invalid quantity!")

def remove_item():
    selected = cart_table.selection()
    if not selected: return
    idx = cart_table.index(selected[0])
    cart.pop(idx)
    refresh_cart()

def checkout():
    global cart
    if not cart:
        messagebox.showerror("Error", "Cart is empty!")
        return

    subtotal = sum(item["price"] * item["quantity"] for item in cart)
    gst = subtotal * 0.05
    total = subtotal + gst

    bill_id = save_bill(cart, total)   # save total with GST
    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate PDF invoice
    filename = generate_invoice(bill_id, cart, total, datetime_str, gst=gst, subtotal=subtotal)
    webbrowser.open_new(filename)

    messagebox.showinfo("Success", f"Bill saved as Invoice #{bill_id}")
    cart = []
    refresh_cart()

# ===== VIEW PAST BILLS =====
def view_bills():
    bills = get_all_bills()
    win = tk.Toplevel(root)
    win.title("Past Bills")

    tree = ttk.Treeview(win, columns=("id", "datetime", "total"), show="headings")
    tree.heading("id", text="Bill ID")
    tree.heading("datetime", text="Date/Time")
    tree.heading("total", text="Total")
    tree.pack(fill="both", expand=True)

    for b in bills:
        tree.insert("", "end", values=(b[0], b[1], f"{b[2]:.2f}"))

    def open_invoice():
        selected = tree.selection()
        if not selected: return
        bill_id = tree.item(selected[0])["values"][0]

        items = get_bill_items(bill_id)
        total = 0
        item_dicts = []

        for i in items:
            try:
                price = float(i[4])
                qty = int(i[5])
                total += price * qty
                item_dicts.append({
                    "barcode": i[2],
                    "name": i[3],
                    "price": price,
                    "quantity": qty
                })
            except ValueError:
                continue

        # Get datetime from bills table
        bills = get_all_bills()
        bill_datetime = next((b[1] for b in bills if b[0] == bill_id), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        filename = generate_invoice(bill_id, item_dicts, total, bill_datetime)
        webbrowser.open_new(filename)

    def show_details():
        selected = tree.selection()
        if not selected: return
        bill_id = tree.item(selected[0])["values"][0]
        show_bill_details(bill_id)

    # Buttons
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Open Invoice", command=open_invoice).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Show Details", command=show_details).grid(row=0, column=1, padx=5)

def show_bill_details(bill_id):
    items = get_bill_items(bill_id)

    win = Toplevel(root)
    win.title(f"Bill #{bill_id}")
    win.geometry("560x380")

    cols = ("Name", "Price", "Qty", "Subtotal")
    items_table = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        items_table.heading(c, text=c)
    items_table.pack(fill="both", expand=True, padx=10, pady=10)

    subtotal = 0.0
    for i in items:
        try:
            name = i[3]
            price = float(i[4])
            qty = int(i[5])
            sub = price * qty
            subtotal += sub
            items_table.insert("", "end", values=(name, f"{price:.2f}", qty, f"{sub:.2f}"))
        except (ValueError, TypeError):
            continue

    gst = subtotal * 0.05
    total = subtotal + gst

    tk.Label(win, text=f"Subtotal: Rs.{subtotal:.2f}", font=("Arial", 12)).pack()
    tk.Label(win, text=f"GST (5%): Rs.{gst:.2f}", font=("Arial", 12)).pack()
    tk.Label(win, text=f"Grand Total: Rs.{total:.2f}", font=("Arial", 14, "bold"), fg="blue").pack(pady=10)

    def reprint():
        item_dicts = []
        for i in items:
            try:
                item_dicts.append({
                    "barcode": i[2],
                    "name": i[3],
                    "price": float(i[4]),
                    "quantity": int(i[5]),
                })
            except (ValueError, TypeError):
                continue
        bill_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = generate_invoice(bill_id, item_dicts, total, bill_datetime, gst=gst, subtotal=subtotal)
        webbrowser.open_new(filename)

    ttk.Button(win, text="Re-Print Invoice", command=reprint).pack(pady=6)

# ===== GUI =====
root = tk.Tk()
root.title("POS Billing System")
root.geometry("700x500")

style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
style.configure("Treeview", font=("Arial", 11), rowheight=25)
style.configure("TButton", font=("Arial", 11), padding=6)

frame = tk.Frame(root, pady=10)
frame.pack(fill="x")

tk.Label(frame, text="Barcode:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
barcode_entry = tk.Entry(frame, font=("Arial", 12), width=30)
barcode_entry.grid(row=0, column=1, padx=5)

def on_enter(event):
    code = barcode_entry.get().strip()
    if code:
        add_to_cart(code)
    barcode_entry.delete(0, tk.END)

barcode_entry.bind("<Return>", on_enter)

cart_table = ttk.Treeview(root, columns=("Name", "Price", "Qty", "Subtotal"), show="headings")
cart_table.pack(fill="both", expand=True, padx=10, pady=10)
for col in ("Name", "Price", "Qty", "Subtotal"):
    cart_table.heading(col, text=col)

total_label = tk.Label(root, text="Total: Rs.0", font=("Arial", 16, "bold"), fg="blue")
total_label.pack(pady=5)

btn_frame = tk.Frame(root, pady=10)
btn_frame.pack()

ttk.Button(btn_frame, text="Edit Price", command=edit_price).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Edit Quantity", command=edit_quantity).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Remove Item", command=remove_item).grid(row=0, column=2, padx=5)
ttk.Button(btn_frame, text="Checkout", command=checkout).grid(row=0, column=3, padx=5)
ttk.Button(btn_frame, text="View Bills", command=view_bills).grid(row=0, column=4, padx=5)

root.mainloop()

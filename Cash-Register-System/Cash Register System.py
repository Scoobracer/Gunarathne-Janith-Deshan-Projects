import datetime
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

class GroceryPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery POS with Loyalty & Discounts")
        self.total = 0
        self.bill_items = []

        # Load items prices
        self.items = {}
        with open("items.txt", "r") as f:
            for line in f:
                name, price = line.strip().split(",")
                self.items[name.lower()] = float(price)

        # Load loyalty customers: mobile -> name
        self.customers = {}
        if os.path.exists("customers.txt"):
            with open("customers.txt", "r") as f:
                for line in f:
                    mob, name = line.strip().split(",")
                    self.customers[mob] = name

        # --- UI Setup ---
        tk.Label(root, text="Grocery POS System", font=("Arial", 18)).pack(pady=10)

        # Loyalty customer input
        loyalty_frame = tk.Frame(root)
        loyalty_frame.pack(pady=5)

        tk.Label(loyalty_frame, text="Mobile Number:").grid(row=0, column=0)
        self.mobile_entry = tk.Entry(loyalty_frame, width=15)
        self.mobile_entry.grid(row=0, column=1)
        self.mobile_entry.bind("<FocusOut>", self.check_loyalty)

        tk.Label(loyalty_frame, text="Customer Name:").grid(row=1, column=0)
        self.customer_name_label = tk.Label(loyalty_frame, text="(Not Found)", fg="red")
        self.customer_name_label.grid(row=1, column=1)

        tk.Label(loyalty_frame, text="Add New Loyalty User:").grid(row=2, column=0, columnspan=2, pady=(10,0))

        tk.Label(loyalty_frame, text="Mobile:").grid(row=3, column=0)
        self.new_mobile_entry = tk.Entry(loyalty_frame, width=15)
        self.new_mobile_entry.grid(row=3, column=1)

        tk.Label(loyalty_frame, text="Name:").grid(row=4, column=0)
        self.new_name_entry = tk.Entry(loyalty_frame, width=15)
        self.new_name_entry.grid(row=4, column=1)

        tk.Button(loyalty_frame, text="Add Loyalty User", command=self.add_loyalty_user).grid(row=5, column=0, columnspan=2, pady=5)

        # Item input
        tk.Label(root, text="Item Name:").pack()
        self.item_entry = tk.Entry(root)
        self.item_entry.pack()
        self.item_entry.bind("<KeyRelease>", self.update_price)

        tk.Label(root, text="Price (LKR):").pack()
        self.price_var = tk.StringVar()
        self.price_entry = tk.Entry(root, textvariable=self.price_var, state="readonly")
        self.price_entry.pack()

        tk.Label(root, text="Quantity:").pack()
        self.qty_entry = tk.Entry(root)
        self.qty_entry.pack()

        tk.Label(root, text="Discount % (per item):").pack()
        self.discount_entry = tk.Entry(root)
        self.discount_entry.insert(0, "0")
        self.discount_entry.pack()

        tk.Button(root, text="Add to Bill", command=self.add_to_bill).pack(pady=10)

        self.bill_area = tk.Text(root, height=15, width=60, font=("Courier", 12))
        self.bill_area.pack()

        self.total_label = tk.Label(root, text="Total: LKR 0.00")
        self.total_label.pack()

        tk.Label(root, text="Total Bill Discount %:").pack()
        self.total_bill_discount_entry = tk.Entry(root)
        self.total_bill_discount_entry.insert(0, "0")
        self.total_bill_discount_entry.pack()

        tk.Button(root, text="Finish & Print Bill", command=self.finish_bill).pack(pady=10)

    def check_loyalty(self, event=None):
        mob = self.mobile_entry.get().strip()
        if mob in self.customers:
            self.customer_name_label.config(text=self.customers[mob], fg="green")
        else:
            self.customer_name_label.config(text="(Not Found)", fg="red")

    def add_loyalty_user(self):
        mob = self.new_mobile_entry.get().strip()
        name = self.new_name_entry.get().strip()
        if not mob or not name:
            messagebox.showwarning("Input Error", "Please enter both mobile and name.")
            return
        if mob in self.customers:
            messagebox.showinfo("Exists", "Customer already exists!")
            return
        self.customers[mob] = name
        with open("customers.txt", "a") as f:
            f.write(f"{mob},{name}\n")
        messagebox.showinfo("Success", f"Loyalty user {name} added.")
        self.new_mobile_entry.delete(0, tk.END)
        self.new_name_entry.delete(0, tk.END)

    def update_price(self, event=None):
        name = self.item_entry.get().strip().lower()
        price = self.items.get(name, "")
        self.price_var.set(price)

    def add_to_bill(self):
        name = self.item_entry.get().strip().lower()
        if not name or not self.price_var.get():
            messagebox.showwarning("Input Error", "Enter valid item name.")
            return
        try:
            qty = int(self.qty_entry.get())
            discount = float(self.discount_entry.get())
            if discount < 0 or discount > 100:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Enter valid quantity and discount (0-100).")
            return

        price = float(self.price_var.get())
        discounted_price = price * (1 - discount / 100)
        line_total = discounted_price * qty

        self.bill_items.append((name, price, qty, discount, discounted_price, line_total))
        self.total += line_total

        self.update_bill()
        # Clear inputs
        self.item_entry.delete(0, tk.END)
        self.price_var.set("")
        self.qty_entry.delete(0, tk.END)
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, "0")

    def update_bill(self):
        self.bill_area.delete(1.0, tk.END)
        for item in self.bill_items:
            self.bill_area.insert(tk.END,
                f"{item[0]:<15} {item[1]:>6.2f} LKR  Qty:{item[2]:<3}  Disc:{item[3]:>5.1f}%  Price after disc: {item[4]:>6.2f}  Line Total: LKR {item[5]:.2f}\n")
        self.total_label.config(text=f"Total: LKR {self.total:.2f}")

    def finish_bill(self):
        if not self.bill_items:
            messagebox.showinfo("Empty Bill", "No items added!")
            return
        try:
            total_discount = float(self.total_bill_discount_entry.get())
            if total_discount < 0 or total_discount > 100:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Enter valid total discount (0-100).")
            return

        total_after_discount = self.total * (1 - total_discount / 100)

        mob = self.mobile_entry.get().strip()
        cust_name = self.customers.get(mob, "Guest")

        bill_text = "===== Grocery Bill =====\n"
        bill_text += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        bill_text += f"Customer: {cust_name}\n\n"
        bill_text += f"{'Item':<15}{'Price':>8}{'Qty':>5}{'Disc%':>7}{'Price After Disc':>18}{'Total':>10}\n"
        bill_text += "-"*70 + "\n"
        for item in self.bill_items:
            bill_text += f"{item[0]:<15}{item[1]:>8.2f}{item[2]:>5}{item[3]:>7.1f}{item[4]:>18.2f}{item[5]:>10.2f}\n"
        bill_text += "-"*70 + "\n"
        bill_text += f"Total Before Discount: LKR {self.total:.2f}\n"
        bill_text += f"Total Discount: {total_discount}%\n"
        bill_text += f"Total After Discount: LKR {total_after_discount:.2f}\n"
        bill_text += "=======================\n"

        # Save bill to file in bills folder
        if not os.path.exists("bills"):
            os.makedirs("bills")
        filename = f"bills/bill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write(bill_text)

        # Show final bill in a popup window
        self.show_bill_popup(bill_text)

        # Reset for next customer
        self.bill_items.clear()
        self.total = 0
        self.mobile_entry.delete(0, tk.END)
        self.customer_name_label.config(text="(Not Found)", fg="red")
        self.item_entry.delete(0, tk.END)
        self.price_var.set("")
        self.qty_entry.delete(0, tk.END)
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, "0")
        self.total_bill_discount_entry.delete(0, tk.END)
        self.total_bill_discount_entry.insert(0, "0")
        self.bill_area.delete(1.0, tk.END)
        self.total_label.config(text="Total: LKR 0.00")

    def show_bill_popup(self, bill_text):
        popup = tk.Toplevel(self.root)
        popup.title("Final Bill")

        st = scrolledtext.ScrolledText(popup, width=80, height=25, font=("Courier", 12))
        st.pack(padx=10, pady=10)
        st.insert(tk.END, bill_text)
        st.config(state=tk.DISABLED)

        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryPOS(root)
    root.mainloop()

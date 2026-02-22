import tkinter as tk 
from tkinter import ttk, messagebox 
import sqlite3 
import datetime as datetime 
import matplotlib.pyplot as plt 
import pandas as pd 
 
# Database class 
class Database: 
    def __init__(self, db): 
        self.conn = sqlite3.connect(db) 
        self.cur = self.conn.cursor() 
        self.cur.execute(""" 
            CREATE TABLE IF NOT EXISTS users ( 
                user_id TEXT PRIMARY KEY, 
                username TEXT 
            ) 
        """) 
        self.cur.execute(""" 
            CREATE TABLE IF NOT EXISTS income_record ( 
                user_id TEXT, 
                income_type TEXT, 
                amount FLOAT, 
                date DATE 
            ) 
        """) 
        self.cur.execute(""" 
            CREATE TABLE IF NOT EXISTS expense_record ( 
                user_id TEXT, 
                item_name TEXT, 
                item_price FLOAT, 
                purchase_date DATE 
            ) 
        """) 
        self.conn.commit() 
 
    def fetchRecord(self, query): 
        self.cur.execute(query) 
        rows = self.cur.fetchall() 
        return rows 

 
    def insertRecord(self, table, values): 
        if table == 'income_record': 
            self.cur.execute(f"INSERT INTO {table} (user_id, income_type, amount, date) 
VALUES (?, ?, ?, ?)", values) 
        elif table == 'expense_record': 
            self.cur.execute(f"INSERT INTO {table} (user_id, item_name, item_price, 
purchase_date) VALUES (?, ?, ?, ?)", values) 
        self.conn.commit() 
 
    def removeRecord(self, table, rwid): 
        self.cur.execute(f"DELETE FROM {table} WHERE rowid=?", (rwid,)) 
        self.conn.commit() 
 
    def updateRecord(self, table, item_name, item_price, purchase_date, rid): 
        if table == 'income_record': 
            self.cur.execute(f"UPDATE {table} SET income_type=?, amount=?, date=? WHERE 
rowid=?", (item_name, item_price, purchase_date, rid)) 
        if table == 'expense_record':    
            self.cur.execute(f"UPDATE {table} SET item_name=?, item_price=?, 
purchase_date=? WHERE rowid=?", (item_name, item_price, purchase_date, rid))   
        self.conn.commit() 
 
    def __del__(self): 
        self.conn.close() 
 
# Create database object 
data = Database('mini.db') 
 
# Login and Registration Functions 
def register(): 
    user_id = user_id_entry.get() 
    username = username_entry.get() 
    if user_id and username: 
        try: 
            data.cur.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, 
username)) 
            data.conn.commit() 
            messagebox.showinfo("Success", "Registration successful!") 
            login_frame.pack_forget() 
            income_frame.pack() 
        except sqlite3.IntegrityError: 
            messagebox.showerror("Error", "User ID already exists.") 
 
    else: 
        messagebox.showerror("Error", "Please fill in all fields.") 
 
def login(): 
    user_id = user_id_entry.get() 
    if user_id: 
        user = data.fetchRecord(f"SELECT * FROM users WHERE user_id='{user_id}'") 
        if user: 
            login_frame.pack_forget() 
            income_frame.pack() 
            refresh_income_records() 
            refresh_expense_records() 
            update_totals() 
        else: 
            messagebox.showerror("Error", "Invalid User ID.") 
    else: 
        messagebox.showerror("Error", "Please enter your User ID.") 
 
def show_incomes(): 
    income_frame.pack() 
    expense_frame.pack_forget() 
    refresh_income_records() 
 
def show_expenses(): 
    expense_frame.pack() 
    income_frame.pack_forget() 
    refresh_expense_records() 
 
def update_totals(): 
    user_id = user_id_entry.get() 
    total_income = sum([record[2] for record in data.fetchRecord(f"SELECT * FROM 
income_record WHERE user_id='{user_id}'")]) 
    total_expense = sum([record[2] for record in data.fetchRecord(f"SELECT * FROM 
expense_record WHERE user_id='{user_id}'")]) 
     
    total_income_label.config(text=f"Total Income: {total_income}") 
    total_expense_label.config(text=f"Total Expenses: {total_expense}") 
 
    if total_expense > total_income: 
        messagebox.showwarning("Warning", "Expenses exceed Income!") 
 
def add_income(): 
 
    income_type = income_type_entry.get() 
    amount = amount_entry.get() 
    date = date_entry.get() 
    user_id = user_id_entry.get()  # Get the user_id of the logged-in user 
     
    if income_type and amount and date: 
        data.insertRecord('income_record', (user_id, income_type, float(amount), date)) 
        messagebox.showinfo("Success", "Income added successfully!") 
        clear_income_entries() 
        refresh_income_records() 
        update_totals() 
    else: 
        messagebox.showerror("Error", "Please fill in all fields.") 
 
def clear_income_entries(): 
    income_type_entry.delete(0, 'end') 
    amount_entry.delete(0, 'end') 
    date_entry.delete(0, 'end') 
 
def refresh_income_records(): 
    for item in income_treeview.get_children(): 
        income_treeview.delete(item) 
    user_id = user_id_entry.get()  # Get the user_id of the logged-in user 
    records = data.fetchRecord(f"SELECT user_id, income_type, amount, date FROM 
income_record WHERE user_id='{user_id}' ORDER BY date ASC") 
    for record in records: 
        income_treeview.insert("", "end", values=(record[0], record[1], record[2], record[3])) 
 
def clear_expense_entries(): 
    expense_name_entry.delete(0, 'end') 
    expense_price_entry.delete(0, 'end') 
    expense_date_entry.delete(0, 'end') 
 
def refresh_expense_records(): 
    for item in expense_treeview.get_children(): 
        expense_treeview.delete(item) 
    user_id = user_id_entry.get()  # Get the user_id of the logged-in user 
    records = data.fetchRecord(f"SELECT user_id, item_name, item_price, purchase_date 
FROM expense_record WHERE user_id='{user_id}' ORDER BY purchase_date ASC") 
    for record in records: 
        expense_treeview.insert("", "end", values=(record[0], record[1], record[2], record[3])) 
 
  
def add_expense(): 
    item_name = expense_name_entry.get() 
    item_price = expense_price_entry.get() 
    purchase_date = expense_date_entry.get() 
    user_id = user_id_entry.get()  # Get the user_id of the logged-in user 
     
    if item_name and item_price and purchase_date: 
        data.insertRecord('expense_record', (user_id, item_name, float(item_price), 
purchase_date)) 
        messagebox.showinfo("Success", "Expense added successfully!") 
        clear_expense_entries() 
        refresh_expense_records() 
        update_totals() 
 
def visualize_data():     
    user_id = user_id_entry.get() 
    income_records = data.fetchRecord(f"SELECT * FROM income_record WHERE 
user_id='{user_id}'") 
    expense_records = data.fetchRecord(f"SELECT * FROM expense_record WHERE 
user_id='{user_id}'") 
 
    income_df = pd.DataFrame(income_records, columns=["user_id", "income_type", 
"amount", "date"]) 
    expense_df = pd.DataFrame(expense_records, columns=["user_id", "item_name", 
"item_price", "purchase_date"]) 
 
    income_df['amount'] = income_df['amount'].astype(float) 
    income_df['date'] = pd.to_datetime(income_df['date']) 
    expense_df['item_price'] = expense_df['item_price'].astype(float) 
    expense_df['purchase_date'] = pd.to_datetime(expense_df['purchase_date']) 
 
    plt.figure(figsize=(12, 6)) 
    plt.bar(['Income', 'Expense'], [income_df['amount'].sum(), expense_df['item_price'].sum()], 
color=['green', 'red'])  
    plt.title('Income vs Expense') 
    plt.ylabel('Amount') 
    plt.show() 
    expense_category_sum = expense_df.groupby('item_name')['item_price'].sum()  
    expense_category_sum.plot(kind='pie', autopct='%1.1f%%', startangle=140, title='Expense 
Distribution by Category') 
    plt.ylabel('')  
    plt.show() 
 
  
def update_income(): 
    selected_item = income_treeview.selection() 
    if selected_item: 
        item_id = income_treeview.item(selected_item, 'values')[0]  # Get the selected row ID 
        income_type = income_type_entry.get() 
        amount = amount_entry.get() 
        date = date_entry.get() 
 
        if income_type and amount and date: 
            data.updateRecord('income_record', income_type, float(amount), date, item_id) 
            messagebox.showinfo("Success", "Income updated successfully!") 
            clear_income_entries() 
            refresh_income_records() 
            update_totals() 
        else: 
            messagebox.showerror("Error", "Please fill in all fields.") 
    else: 
        messagebox.showwarning("Warning", "Please select an entry to update.") 
 
def update_expense(): 
    selected_item = expense_treeview.selection() 
    if selected_item: 
        item_id = expense_treeview.item(selected_item, 'values')[0]  # Get the selected row ID 
        item_name = expense_name_entry.get() 
        item_price = expense_price_entry.get() 
        purchase_date = expense_date_entry.get() 
 
        if item_name and item_price and purchase_date: 
            data.updateRecord('expense_record', item_name, float(item_price), purchase_date, 
item_id) 
            messagebox.showinfo("Success", "Expense updated successfully!") 
            clear_expense_entries() 
            refresh_expense_records() 
            update_totals() 
        else: 
            messagebox.showerror("Error", "Please fill in all fields.") 
    else: 
        messagebox.showwarning("Warning", "Please select an entry to update.") 
 
# Create main application window 
app = tk.Tk() 
app.title("Finance Tracker") 

 
# Login Frame 
login_frame = tk.Frame(app) 
login_frame.pack() 
tk.Label(login_frame, text="User ID").grid(row=0, column=0) 
user_id_entry = tk.Entry(login_frame) 
user_id_entry.grid(row=0, column=1) 
tk.Label(login_frame, text="Username").grid(row=1, column=0) 
username_entry = tk.Entry(login_frame) 
username_entry.grid(row=1, column=1) 
tk.Button(login_frame, text="Register", command=register).grid(row=2, column=0) 
tk.Button(login_frame, text="Login", command=login).grid(row=2, column=1) 
 
# Income Frame 
income_frame = tk.Frame(app) 
tk.Label(income_frame, text="Income Type").grid(row=0, column=0) 
income_type_entry = tk.Entry(income_frame) 
income_type_entry.grid(row=0, column=1) 
tk.Label(income_frame, text="Amount").grid(row=1, column=0) 
amount_entry = tk.Entry(income_frame) 
amount_entry.grid(row=1, column=1) 
tk.Label(income_frame, text="Date").grid(row=2, column=0) 
date_entry = tk.Entry(income_frame) 
date_entry.grid(row=2, column=1) 
tk.Button(income_frame, text="Add Income", bg='#04C4D9', 
command=add_income).grid(row=3, column=0) 
tk.Button(income_frame, text="Update Income", bg='#04C4D9', 
command=update_income).grid(row=3, column=1) 
tk.Button(income_frame, text="Show Expenses", bg='#04C4D9', 
command=show_expenses).grid(row=3, column=2) 
 
income_treeview = ttk.Treeview(income_frame, columns=("User ID", "Income Type", 
"Amount", "Date"), show='headings') 
income_treeview.grid(row=4, column=0, columnspan=3) 
income_treeview.heading("User ID", text="User ID") 
income_treeview.heading("Income Type", text="Income Type") 
income_treeview.heading("Amount", text="Amount") 
income_treeview.heading("Date", text="Date") 
 
# Total Income Label 
total_income_label = tk.Label(income_frame, text="Total Income: 0") 
total_income_label.grid(row=5, columnspan=3) 

# Expense Frame 
expense_frame = tk.Frame(app) 
tk.Label(expense_frame, text="Item Name").grid(row=0, column=0) 
expense_name_entry = tk.Entry(expense_frame) 
expense_name_entry.grid(row=0, column=1) 
tk.Label(expense_frame, text="Item Price").grid(row=1, column=0) 
expense_price_entry = tk.Entry(expense_frame) 
expense_price_entry.grid(row=1, column=1) 
tk.Label(expense_frame, text="Purchase Date").grid(row=2, column=0) 
expense_date_entry = tk.Entry(expense_frame) 
expense_date_entry.grid(row=2, column=1) 
tk.Button(expense_frame, text="Add Expense", bg='#C2BB00', 
command=add_expense).grid(row=3, column=0) 
tk.Button(expense_frame, text="Update Expense", bg='#C2BB00', 
command=update_expense).grid(row=3, column=1) 
tk.Button(expense_frame, text="Show Income", bg='#C2BB00', 
command=show_incomes).grid(row=3, column=2) 
tk.Button(expense_frame, text="Visualize Data", bg='#C2BB00', 
command=visualize_data).grid(row=34, column=1) 
 
expense_treeview = ttk.Treeview(expense_frame, columns=("User ID", "Item Name", "Item 
Price", "Purchase Date"), show='headings') 
expense_treeview.grid(row=4, column=0, columnspan=3) 
expense_treeview.heading("User ID", text="User ID") 
expense_treeview.heading("Item Name", text="Item Name") 
expense_treeview.heading("Item Price", text="Item Price") 
expense_treeview.heading("Purchase Date", text="Purchase Date") 
 
# Total Expense Label 
total_expense_label = tk.Label(expense_frame, text="Total Expenses: 0") 
total_expense_label.grid(row=5, columnspan=3) 
 
# Start the application 
app.mainloop() 

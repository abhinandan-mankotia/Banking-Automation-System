from tkinter import Tk, Label, Frame, Entry, Button, messagebox, filedialog
from tkinter.ttk import Combobox
import time
from PIL import Image, ImageTk
import random
import sqlite3
from tkintertable import TableCanvas, TableModel
import re
import shutil
import os

# --- MODERN COLOR PALETTE ---
BG_COLOR = "#F8FAFC"        # Light Slate (Background)
FRAME_BG = "#FFFFFF"        # Pure White (Cards/Frames)
PRIMARY = "#4F46E5"         # Vibrant Indigo (Headers/Main Buttons)
SUCCESS = "#10B981"         # Emerald Green (Deposit/Create)
DANGER = "#F43F5E"          # Rose Red (Withdraw/Delete)
TEXT_DARK = "#0F172A"       # Dark Slate (Main Text)
TEXT_LIGHT = "#FFFFFF"      # White (Button Text)
ACCENT = "#38BDF8"          # Light Blue

# --- Database Initialization ---
def init_db():
    with sqlite3.connect('bank.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            users_acno INTEGER PRIMARY KEY AUTOINCREMENT,
                            users_pass TEXT, users_name TEXT, users_mob TEXT,
                            users_email TEXT, users_bal REAL, users_adhar TEXT,
                            users_opendate TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS txn (
                            txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            txn_acno INTEGER, txn_type TEXT, txn_date TEXT,
                            txn_amt REAL, txn_updatebal REAL)''')
        conn.commit()

init_db()

# --- Mock Email Function (For Demo/Portfolio Purposes) ---
def mock_send_email(to_email, subject, body):
    # Instead of sending a real email, we print it to the console and return True.
    print("\n" + "="*40)
    print(f"📧 MOCK EMAIL DISPATCHED")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print("-" * 40)
    print(body)
    print("="*40 + "\n")
    return True

# --- Main Window Setup ---
win = Tk()
win.title('Modern Banking Automation System')
win.state('zoomed')
win.resizable(width=False, height=False)
win.configure(bg=BG_COLOR)

# --- Headers & Footers ---
header_title = Label(win, text="Banking Automation", font=('Segoe UI', 45, 'bold'), bg=BG_COLOR, fg=PRIMARY)
header_title.pack(pady=(20, 0))

current_date = time.strftime('%d-%b-%Y')
header_date = Label(win, text=f'Today: {current_date}', font=('Segoe UI', 16), bg=BG_COLOR, fg=TEXT_DARK)
header_date.pack(pady=5)

disclaimer_label = Label(win, text="Disclaimer: This project is for practice purposes only and has no link to the real world.", font=('Segoe UI', 10, 'italic'), bg=BG_COLOR, fg=DANGER)
disclaimer_label.pack(side='bottom', pady=10)

footer_title = Label(win, text="By: Abhinandan Mankotia\nEmail: rabhinandan03@gmail.com", font=('Segoe UI', 14, 'bold'), bg=BG_COLOR, fg=TEXT_DARK)
footer_title.pack(side='bottom', pady=5)

# Graceful Image Loading
try:
    img = Image.open('logo.png').resize((200, 100))
    bitmap_img = ImageTk.PhotoImage(img, master=win)
    logo_label = Label(win, image=bitmap_img, bg=BG_COLOR)
    logo_label.place(relx=0.02, rely=0.02)
except FileNotFoundError:
    logo_label = Label(win, text="[Logo Space]", bg=FRAME_BG, fg=TEXT_DARK, width=20, height=5, font=('Segoe UI', 10))
    logo_label.place(relx=0.02, rely=0.02)

def main_screen():
    frm = Frame(win, bg=FRAME_BG, highlightbackground=ACCENT, highlightthickness=2)
    frm.place(relx=0.15, rely=0.2, relwidth=0.7, relheight=0.6)

    global cap
    cap = ''
    
    def generate_captcha():
        global cap
        cap = str(random.randint(0, 9)) + chr(random.randint(65, 90)) + \
              str(random.randint(0, 9)) + chr(random.randint(65, 90))
        return cap
    
    def reset():
        acn_entry.delete(0, "end")
        pass_entry.delete(0, "end")
        captcha_entry.delete(0, "end")
        acn_entry.focus()

    def login_click():
        global uacn, uname
        uacn_val = acn_entry.get()
        upass = pass_entry.get()
        urole = role_cb.get()

        if len(uacn_val) == 0 or len(upass) == 0:
            messagebox.showerror("Login", "ACN or Password can't be empty")
            return
        if captcha_entry.get() != cap:
            messagebox.showerror("Login", "Invalid captcha")
            return

        try:
            uacn_val = int(uacn_val)
        except ValueError:
            messagebox.showerror("Login", "ACN must be a number")
            return

        if uacn_val == 0 and upass == 'admin' and urole == 'Admin':
            frm.destroy()
            welcome_admin_screen()
        elif urole == 'User':
            with sqlite3.connect('bank.sqlite') as con_obj:
                cur_obj = con_obj.cursor()
                cur_obj.execute('SELECT * FROM users WHERE users_acno=? AND users_pass=?', (uacn_val, upass))
                tup = cur_obj.fetchone()
                
            if tup is None:
                messagebox.showerror('Login', 'Invalid ACN/Password')
            else:
                uname = tup[2]
                uacn = uacn_val
                frm.destroy()
                welcome_user_screen()
        else:
            messagebox.showerror('Login', 'Invalid Role')

    # --- Login UI Components ---
    Label(frm, font=('Segoe UI', 18, 'bold'), bg=FRAME_BG, fg=TEXT_DARK, text="Login to Your Account").place(relx=0.35, rely=0.05)

    Label(frm, font=('Segoe UI', 16), bg=FRAME_BG, text="Account Number (ACN)").place(relx=0.15, rely=0.2)
    acn_entry = Entry(frm, font=('Segoe UI', 16), bg=BG_COLOR, relief="flat", highlightthickness=1, highlightbackground=ACCENT)
    acn_entry.place(relx=0.45, rely=0.2, relwidth=0.4)
    acn_entry.focus()

    Label(frm, font=('Segoe UI', 16), bg=FRAME_BG, text="Password").place(relx=0.15, rely=0.35)
    pass_entry = Entry(frm, font=('Segoe UI', 16), bg=BG_COLOR, relief="flat", highlightthickness=1, highlightbackground=ACCENT, show='*')
    pass_entry.place(relx=0.45, rely=0.35, relwidth=0.4)

    Label(frm, font=('Segoe UI', 16), bg=FRAME_BG, text="Role").place(relx=0.15, rely=0.5)
    role_cb = Combobox(frm, font=('Segoe UI', 16), values=['User', 'Admin'], state="readonly")
    role_cb.current(0)
    role_cb.place(relx=0.45, rely=0.5, relwidth=0.4)

    # --- FIXED: 'strike' changed to 'overstrike' ---
    Label(frm, font=('Segoe UI', 18, 'bold', 'overstrike'), bg=BG_COLOR, fg=PRIMARY, text=generate_captcha(), width=8).place(relx=0.25, rely=0.65)

    Label(frm, font=('Segoe UI', 16), bg=FRAME_BG, text="Enter Captcha").place(relx=0.45, rely=0.65)
    captcha_entry = Entry(frm, font=('Segoe UI', 16), bg=BG_COLOR, relief="flat", highlightthickness=1, highlightbackground=ACCENT)
    captcha_entry.place(relx=0.6, rely=0.65, relwidth=0.25)

    Button(frm, text='Login', font=('Segoe UI', 16, 'bold'), bg=PRIMARY, fg=TEXT_LIGHT, relief="flat", command=login_click).place(relx=0.3, rely=0.85, relwidth=0.15)
    Button(frm, command=reset, text='Reset', font=('Segoe UI', 16, 'bold'), bg=BG_COLOR, fg=TEXT_DARK, relief="flat", highlightthickness=1, highlightbackground=TEXT_DARK).place(relx=0.5, rely=0.85, relwidth=0.15)
    Button(frm, command=forgot_password_screen, text='Forgot Password?', font=('Segoe UI', 12, 'underline'), bg=FRAME_BG, fg=PRIMARY, relief="flat", bd=0).place(relx=0.7, rely=0.86)

def welcome_admin_screen():
    frm = Frame(win, bg=FRAME_BG, highlightbackground=ACCENT, highlightthickness=2)
    frm.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.6)

    def logout_click():
        if messagebox.askyesno('Logout', 'Do you want to logout?'):
            frm.destroy()
            main_screen()
    
    def create_click():
        ifrm = Frame(frm, bg=BG_COLOR)
        ifrm.place(relx=0.25, rely=0.1, relwidth=0.7, relheight=0.8)

        def open_acn():
            uname = name_entry.get()
            umob = mob_entry.get()
            uemail = email_entry.get()
            uadhar = adhar_entry.get()
            upass = str(random.randint(100000, 999999))

            if not (uname and umob and uemail and uadhar):
                messagebox.showerror('Create', 'Empty fields are not allowed')
                return
            if not re.fullmatch('[a-zA-Z ]+', uname):
                messagebox.showerror('Create', 'Enter valid name')
                return
            if not re.fullmatch('[6-9][0-9]{9}', umob):
                messagebox.showerror('Create', 'Enter valid 10-digit mobile number')
                return
            if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', uemail):
                messagebox.showerror('Create', 'Enter valid email')
                return
            if not re.fullmatch('[0-9]{12}', uadhar):
                messagebox.showerror('Create', 'Enter valid 12-digit Aadhar')
                return

            with sqlite3.connect('bank.sqlite') as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users(users_pass,users_name,users_mob,users_email,users_bal,users_adhar,users_opendate) VALUES(?,?,?,?,?,?,?)',
                            (upass, uname, umob, uemail, 0, uadhar, current_date))
                new_acn = cur.lastrowid
            
            umsg = f"Hello {uname},\nWelcome to ABC Bank.\nYour ACN is: {new_acn}\nYour Pass is: {upass}\nKindly change your password when you login."
            
            # --- Using Mock Email ---
            mock_send_email(uemail, 'Account Opened', umsg)
            messagebox.showinfo('Success', f'Mock Email Sent! Check console.\n\nAccount Created for {uname}.\nACN: {new_acn}\nPass: {upass}')

        Label(ifrm, font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=PRIMARY, text="Create New User").pack(pady=10)

        Label(ifrm, font=('Segoe UI', 14), bg=BG_COLOR, text="Full Name").place(relx=0.1, rely=0.2)
        name_entry = Entry(ifrm, font=('Segoe UI', 14), relief="flat")
        name_entry.place(relx=0.1, rely=0.27, relwidth=0.35)

        Label(ifrm, font=('Segoe UI', 14), bg=BG_COLOR, text="Mobile Number").place(relx=0.1, rely=0.45)
        mob_entry = Entry(ifrm, font=('Segoe UI', 14), relief="flat")
        mob_entry.place(relx=0.1, rely=0.52, relwidth=0.35)

        Label(ifrm, font=('Segoe UI', 14), bg=BG_COLOR, text="Email Address").place(relx=0.55, rely=0.2)
        email_entry = Entry(ifrm, font=('Segoe UI', 14), relief="flat")
        email_entry.place(relx=0.55, rely=0.27, relwidth=0.35)

        Label(ifrm, font=('Segoe UI', 14), bg=BG_COLOR, text="Aadhar Number").place(relx=0.55, rely=0.45)
        adhar_entry = Entry(ifrm, font=('Segoe UI', 14), relief="flat")
        adhar_entry.place(relx=0.55, rely=0.52, relwidth=0.35)

        Button(ifrm, command=open_acn, text='Create Account', font=('Segoe UI', 16, 'bold'), bg=SUCCESS, fg=TEXT_LIGHT, relief="flat").place(relx=0.35, rely=0.75, relwidth=0.3)

    def view_click():
        ifrm = Frame(frm, bg=BG_COLOR)
        ifrm.place(relx=0.25, rely=0.1, relwidth=0.7, relheight=0.8)
        Label(ifrm, font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=PRIMARY, text="View All Users").pack(pady=10)

        frame = Frame(ifrm)
        frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.8)

        data = {}
        with sqlite3.connect('bank.sqlite') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            for i, tup in enumerate(cur, 1):
                data[str(i)] = {"Acno": tup[0], "Email": tup[4], "Mob": tup[3], "Balance": tup[5], "Adhar": tup[6], "Date": tup[7]}

        model = TableModel()
        model.importDict(data)
        table = TableCanvas(frame, model=model, editable=False)
        table.show()

    def delete_click():
        ifrm = Frame(frm, bg=BG_COLOR)
        ifrm.place(relx=0.25, rely=0.1, relwidth=0.7, relheight=0.8)
        Label(ifrm, font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=DANGER, text="Delete User Account").pack(pady=10)

        def delete_db():
            target_acn = acn_entry.get()
            if not target_acn: return
            with sqlite3.connect('bank.sqlite') as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM users WHERE users_acno=?", (target_acn,))
                cur.execute("DELETE FROM txn WHERE txn_acno=?", (target_acn,))
            messagebox.showinfo("Deleted", f"User ACN {target_acn} successfully deleted.")
            acn_entry.delete(0, 'end')

        Label(ifrm, font=('Segoe UI', 16), bg=BG_COLOR, text="Target Account Number (ACN)").place(relx=0.3, rely=0.3)
        acn_entry = Entry(ifrm, font=('Segoe UI', 16), relief="flat")
        acn_entry.place(relx=0.3, rely=0.4, relwidth=0.4)
        Button(ifrm, command=delete_db, text='Permanently Delete', font=('Segoe UI', 16, 'bold'), bg=DANGER, fg=TEXT_LIGHT, relief="flat").place(relx=0.35, rely=0.6, relwidth=0.3)

    Label(frm, font=('Segoe UI', 22, 'bold'), bg=FRAME_BG, fg=PRIMARY, text="Admin Dashboard").place(relx=0.02, rely=0.02)
    Button(frm, command=logout_click, text='Logout', font=('Segoe UI', 14, 'bold'), bg=BG_COLOR, fg=TEXT_DARK, relief="flat").place(relx=0.88, rely=0.02)

    Button(frm, command=create_click, text='Create User', font=('Segoe UI', 14, 'bold'), bg=PRIMARY, fg=TEXT_LIGHT, relief="flat").place(relx=0.02, rely=0.2, relwidth=0.2)
    Button(frm, command=view_click, text='View Users', font=('Segoe UI', 14, 'bold'), bg=ACCENT, fg=TEXT_DARK, relief="flat").place(relx=0.02, rely=0.35, relwidth=0.2)
    Button(frm, command=delete_click, text='Delete User', font=('Segoe UI', 14, 'bold'), bg=DANGER, fg=TEXT_LIGHT, relief="flat").place(relx=0.02, rely=0.5, relwidth=0.2)

def forgot_password_screen():
    frm = Frame(win, bg=FRAME_BG, highlightbackground=ACCENT, highlightthickness=2)
    frm.place(relx=0.25, rely=0.2, relwidth=0.5, relheight=0.6)

    def back_click():
        frm.destroy()
        main_screen()

    def get_password():
        facn = acn_entry.get()
        fmob = mob_entry.get()
        femail = email_entry.get()

        with sqlite3.connect('bank.sqlite') as conn:
            cur = conn.cursor()
            cur.execute('SELECT users_name, users_pass FROM users WHERE users_acno=? AND users_email=? AND users_mob=?', (facn, femail, fmob))
            tup = cur.fetchone()

        if tup is None:
            messagebox.showerror('Forgot Pass', 'Invalid Details. Could not verify identity.')
        else:
            umsg = f"Hello {tup[0]},\nWelcome back to ABC Bank.\nYour Pass is: {tup[1]}\nThanks."
            # --- Using Mock Email ---
            mock_send_email(femail, 'Password Recovery', umsg)
            messagebox.showinfo('Success', f'Mock Password Recovery Sent to {femail}!\nCheck your console output.')

    Button(frm, command=back_click, text='← Back', font=('Segoe UI', 14), bg=BG_COLOR, fg=TEXT_DARK, relief="flat").place(relx=0.02, rely=0.02)
    Label(frm, font=('Segoe UI', 20, 'bold'), bg=FRAME_BG, fg=PRIMARY, text="Recover Password").place(relx=0.3, rely=0.1)

    Label(frm, font=('Segoe UI', 14), bg=FRAME_BG, text="ACN").place(relx=0.2, rely=0.3)
    acn_entry = Entry(frm, font=('Segoe UI', 14), bg=BG_COLOR, relief="flat")
    acn_entry.place(relx=0.4, rely=0.3, relwidth=0.4)

    Label(frm, font=('Segoe UI', 14), bg=FRAME_BG, text="Email").place(relx=0.2, rely=0.45)
    email_entry = Entry(frm, font=('Segoe UI', 14), bg=BG_COLOR, relief="flat")
    email_entry.place(relx=0.4, rely=0.45, relwidth=0.4)

    Label(frm, font=('Segoe UI', 14), bg=FRAME_BG, text="Mobile").place(relx=0.2, rely=0.6)
    mob_entry = Entry(frm, font=('Segoe UI', 14), bg=BG_COLOR, relief="flat")
    mob_entry.place(relx=0.4, rely=0.6, relwidth=0.4)

    Button(frm, command=get_password, text='Recover', font=('Segoe UI', 16, 'bold'), bg=PRIMARY, fg=TEXT_LIGHT, relief="flat").place(relx=0.4, rely=0.8, relwidth=0.2)

def welcome_user_screen():
    frm = Frame(win, bg=FRAME_BG, highlightbackground=ACCENT, highlightthickness=2)
    frm.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.6)

    try:
        if os.path.exists(f"{uacn}.png"):
            img = ImageTk.PhotoImage(Image.open(f'{uacn}.png').resize((150, 150)), master=win)
        else:
            img = ImageTk.PhotoImage(Image.open('default.png').resize((150, 150)), master=win)
        pic_label = Label(frm, image=img, bg=FRAME_BG)
        pic_label.image = img
        pic_label.place(relx=0.03, rely=0.05)
    except FileNotFoundError:
        pic_label = Label(frm, text="[Profile Pic]", width=15, height=7, bg=BG_COLOR, font=('Segoe UI', 12))
        pic_label.place(relx=0.03, rely=0.05)

    def update_photo():
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            shutil.copy(path, f"{uacn}.png")
            img = ImageTk.PhotoImage(Image.open(path).resize((150, 150)), master=win)
            pic_label.configure(image=img)
            pic_label.image = img

    Button(frm, text="Upload Photo", font=('Segoe UI', 10), bg=BG_COLOR, relief="flat", command=update_photo).place(relx=0.04, rely=0.35, relwidth=0.1)

    def logout_click():
        if messagebox.askyesno('Logout', 'Do you want to logout?'):
            frm.destroy()
            main_screen()

    def check_click():
        ifrm = Frame(frm, bg=BG_COLOR)
        ifrm.place(relx=0.2, rely=0.1, relwidth=0.75, relheight=0.8)
        Label(ifrm, font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=PRIMARY, text="Account Overview").pack(pady=10)

        with sqlite3.connect('bank.sqlite') as conn:
            cur = conn.cursor()
            cur.execute('SELECT users_bal, users_opendate, users_adhar FROM users WHERE users_acno=?', (uacn,))
            tup = cur.fetchone()

        Label(ifrm, text=f'Available Balance:', fg=TEXT_DARK, font=('Segoe UI', 16), bg=BG_COLOR).place(relx=0.2, rely=0.3)
        Label(ifrm, text=f'₹ {tup[0]:.2f}', fg=SUCCESS, font=('Segoe UI', 24, 'bold'), bg=BG_COLOR).place(relx=0.5, rely=0.28)
        
        Label(ifrm, text=f'Account Opened: {tup[1]}', fg=TEXT_DARK, font=('Segoe UI', 14), bg=BG_COLOR).place(relx=0.2, rely=0.5)
        Label(ifrm, text=f'Aadhar Number: {tup[2]}', fg=TEXT_DARK, font=('Segoe UI', 14), bg=BG_COLOR).place(relx=0.2, rely=0.6)

    def deposit_click():
        ifrm = Frame(frm, bg=BG_COLOR)
        ifrm.place(relx=0.2, rely=0.1, relwidth=0.75, relheight=0.8)
        Label(ifrm, font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=SUCCESS, text="Deposit Funds").pack(pady=10)

        def deposit_db():
            try:
                uamt = float(amt_entry.get())
                if uamt <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid positive amount")
                return

            with sqlite3.connect('bank.sqlite') as conn:
                cur = conn.cursor()
                cur.execute('SELECT users_bal FROM users WHERE users_acno=?', (uacn,))
                ubal = cur.fetchone()[0]
                
                cur.execute('UPDATE users SET users_bal=users_bal+? WHERE users_acno=?', (uamt, uacn))
                cur.execute('INSERT INTO txn(txn_acno,txn_type,txn_date,txn_amt,txn_updatebal) VALUES(?,?,?,?,?)',
                            (uacn, 'Cr(+)', time.strftime('%d-%b-%Y %r'), uamt, ubal + uamt))
                
            messagebox.showinfo("Deposit Success", f"₹{uamt} successfully deposited.\nNew Balance: ₹{ubal + uamt}")
            amt_entry.delete(0, 'end')

        Label(ifrm, font=('Segoe UI', 16), bg=BG_COLOR, text="Amount (₹)").place(relx=0.3, rely=0.3)
        amt_entry = Entry(ifrm, font=('Segoe UI', 20), relief="flat")
        amt_entry.place(relx=0.3, rely=0.4, relwidth=0.4)
        Button(ifrm, command=deposit_db, text='Confirm Deposit', font=('Segoe UI', 16, 'bold'), bg=SUCCESS, fg=TEXT_LIGHT, relief="flat").place(relx=0.35, rely=0.6, relwidth=0.3)

    def withdraw_click():
        ifrm = Frame(frm, bg=BG_COLOR)
        ifrm.place(relx=0.2, rely=0.1, relwidth=0.75, relheight=0.8)
        Label(ifrm, font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=DANGER, text="Withdraw Funds").pack(pady=10)

        def withdraw_db():
            try:
                uamt = float(amt_entry.get())
                if uamt <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid positive amount")
                return

            with sqlite3.connect('bank.sqlite') as conn:
                cur = conn.cursor()
                cur.execute('SELECT users_bal FROM users WHERE users_acno=?', (uacn,))
                ubal = cur.fetchone()[0]

                if ubal >= uamt:
                    cur.execute('UPDATE users SET users_bal=users_bal-? WHERE users_acno=?', (uamt, uacn))
                    cur.execute('INSERT INTO txn(txn_acno,txn_type,txn_date,txn_amt,txn_updatebal) VALUES(?,?,?,?,?)',
                                (uacn, 'Db(-)', time.strftime('%d-%b-%Y %r'), uamt, ubal - uamt))
                    messagebox.showinfo("Withdraw Success", f"₹{uamt} successfully withdrawn.\nNew Balance: ₹{ubal - uamt}")
                    amt_entry.delete(0, 'end')
                else:
                    messagebox.showerror("Withdraw Failed", "Insufficient Balance")

        Label(ifrm, font=('Segoe UI', 16), bg=BG_COLOR, text="Amount (₹)").place(relx=0.3, rely=0.3)
        amt_entry = Entry(ifrm, font=('Segoe UI', 20), relief="flat")
        amt_entry.place(relx=0.3, rely=0.4, relwidth=0.4)
        Button(ifrm, command=withdraw_db, text='Confirm Withdraw', font=('Segoe UI', 16, 'bold'), bg=DANGER, fg=TEXT_LIGHT, relief="flat").place(relx=0.35, rely=0.6, relwidth=0.3)

    def history_click():
        ifrm = Frame(frm, bg=BG_COLOR)
        ifrm.place(relx=0.2, rely=0.1, relwidth=0.75, relheight=0.8)
        Label(ifrm, font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=PRIMARY, text="Transaction Ledger").pack(pady=10)

        frame = Frame(ifrm)
        frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.8)

        data = {}
        with sqlite3.connect('bank.sqlite') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM txn WHERE txn_acno=?", (uacn,))
            for i, tup in enumerate(cur, 1):
                data[str(i)] = {"Txn Id": tup[0], "Type": tup[2], "Date": tup[3], "Amount": f"₹ {tup[4]}", "Updated Bal": f"₹ {tup[5]}"}

        model = TableModel()
        model.importDict(data)
        table = TableCanvas(frame, model=model, editable=False)
        table.show()

    Label(frm, font=('Segoe UI', 18, 'bold'), bg=FRAME_BG, fg=TEXT_DARK, text=f"Welcome, {uname}").place(relx=0.2, rely=0.02)
    Button(frm, command=logout_click, text='Logout', font=('Segoe UI', 14, 'bold'), bg=BG_COLOR, fg=TEXT_DARK, relief="flat").place(relx=0.88, rely=0.02)

    Button(frm, command=check_click, text='Balance', font=('Segoe UI', 12, 'bold'), bg=PRIMARY, fg=TEXT_LIGHT, relief="flat").place(relx=0.02, rely=0.45, relwidth=0.15)
    Button(frm, command=deposit_click, text='Deposit', font=('Segoe UI', 12, 'bold'), bg=SUCCESS, fg=TEXT_LIGHT, relief="flat").place(relx=0.02, rely=0.55, relwidth=0.15)
    Button(frm, command=withdraw_click, text='Withdraw', font=('Segoe UI', 12, 'bold'), bg=DANGER, fg=TEXT_LIGHT, relief="flat").place(relx=0.02, rely=0.65, relwidth=0.15)
    Button(frm, command=history_click, text='History', font=('Segoe UI', 12, 'bold'), bg=ACCENT, fg=TEXT_DARK, relief="flat").place(relx=0.02, rely=0.75, relwidth=0.15)

main_screen()
win.mainloop()
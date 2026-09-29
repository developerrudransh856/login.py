import datetime
import threading
import time
import tkinter as tk
from tkinter import messagebox
from flask import Flask, jsonify, request
import jwt
import requests
from werkzeug.security import check_password_hash, generate_password_hash

# ==========================================
# 1. FLASK BACKEND API
# ==========================================

flask_app = Flask(__name__)
flask_app.config["SECRET_KEY"] = "instagram_single_file_secret_key"

# Simulated database with hashed passwords
USER_DATABASE = {
    "instagram_user": {
        "password_hash": generate_password_hash("Pass123!"),
        "email": "user@example.com",
        "full_name": "Instagram User",
    }
}


def create_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    return jwt.encode(
        payload, flask_app.config["SECRET_KEY"], algorithm="HS256"
    )


@flask_app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Please enter both username and password.",
                }
            ),
            400,
        )

    # Match username or email
    user = None
    matched_uname = None
    for uname, details in USER_DATABASE.items():
        if (
            uname.lower() == username.lower()
            or details["email"].lower() == username.lower()
        ):
            user = details
            matched_uname = uname
            break

    if not user or not check_password_hash(user["password_hash"], password):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Sorry, your password was incorrect. Please double-check your password.",
                }
            ),
            401,
        )

    token = create_token(matched_uname)
    return (
        jsonify(
            {
                "status": "success",
                "message": "Logged in successfully!",
                "token": token,
                "user": {
                    "username": matched_uname,
                    "full_name": user["full_name"],
                },
            }
        ),
        200,
    )


@flask_app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    identifier = data.get("identifier", "").strip()

    if not identifier:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Please enter your username or email.",
                }
            ),
            400,
        )

    for uname, details in USER_DATABASE.items():
        if (
            uname.lower() == identifier.lower()
            or details["email"].lower() == identifier.lower()
        ):
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"Password reset link sent to registered email ({details['email']}).",
                    }
                ),
                200,
            )

    return (
        jsonify(
            {
                "status": "error",
                "message": "No account found with those credentials.",
            }
        ),
        404,
    )


def run_flask():
    """Runs Flask server in background thread without standard console logs."""
    import logging

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    flask_app.run(port=5000, debug=False, use_reloader=False)


# ==========================================
# 2. TKINTER DESKTOP GUI FRONTEND
# ==========================================

API_URL = "http://127.0.0.1:5000/api"


class InstagramLoginPage:

    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Login")
        self.root.geometry("380x480")
        self.root.configure(bg="#fafafa")
        self.root.resizable(False, False)

        # Main Login Container Card
        self.card = tk.Frame(
            root,
            bg="#ffffff",
            bd=1,
            relief="solid",
            highlightbackground="#dbdbdb",
            highlightthickness=1,
        )
        self.card.place(
            relx=0.5, rely=0.5, anchor="center", width=340, height=420
        )

        # App Brand Title
        self.title_label = tk.Label(
            self.card,
            text="Instagram",
            font=("Arial", 28, "bold"),
            bg="#ffffff",
            fg="#262626",
        )
        self.title_label.pack(pady=(30, 20))

        # Username Input
        self.username_entry = tk.Entry(
            self.card,
            font=("Arial", 10),
            bg="#fafafa",
            fg="#262626",
            bd=1,
            relief="solid",
            highlightthickness=0,
        )
        self.username_entry.insert(0, "Phone number, username, or email")
        self.username_entry.bind("<FocusIn>", self.clear_username_placeholder)
        self.username_entry.bind("<FocusOut>", self.add_username_placeholder)
        self.username_entry.pack(fill="x", padx=30, pady=(0, 10), ipady=7)

        # Password Input
        self.password_entry = tk.Entry(
            self.card,
            font=("Arial", 10),
            bg="#fafafa",
            fg="#262626",
            bd=1,
            relief="solid",
            highlightthickness=0,
        )
        self.password_entry.insert(0, "Password")
        self.password_entry.bind("<FocusIn>", self.clear_password_placeholder)
        self.password_entry.bind("<FocusOut>", self.add_password_placeholder)
        self.password_entry.pack(fill="x", padx=30, pady=(0, 15), ipady=7)

        # Login Button
        self.login_button = tk.Button(
            self.card,
            text="Log In",
            font=("Arial", 10, "bold"),
            bg="#0095f6",
            fg="#ffffff",
            activebackground="#1877f2",
            activeforeground="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.handle_login,
        )
        self.login_button.pack(fill="x", padx=30, pady=(0, 20), ipady=5)

        # Divider
        self.divider_frame = tk.Frame(self.card, bg="#ffffff")
        self.divider_frame.pack(fill="x", padx=30, pady=(0, 15))

        tk.Frame(self.divider_frame, bg="#dbdbdb", height=1).pack(
            side="left", fill="x", expand=True
        )
        tk.Label(
            self.divider_frame,
            text=" OR ",
            font=("Arial", 9, "bold"),
            fg="#8e8e8e",
            bg="#ffffff",
        ).pack(side="left")
        tk.Frame(self.divider_frame, bg="#dbdbdb", height=1).pack(
            side="left", fill="x", expand=True
        )

        # Forgot Password Link
        self.forgot_pwd_label = tk.Label(
            self.card,
            text="Forgot password?",
            font=("Arial", 9),
            fg="#00376b",
            bg="#ffffff",
            cursor="hand2",
        )
        self.forgot_pwd_label.pack(pady=(5, 0))
        self.forgot_pwd_label.bind("<Button-1>", self.handle_forgot_password)

    # Placeholder Handlers
    def clear_username_placeholder(self, event):
        if self.username_entry.get() == "Phone number, username, or email":
            self.username_entry.delete(0, tk.END)

    def add_username_placeholder(self, event):
        if not self.username_entry.get():
            self.username_entry.insert(0, "Phone number, username, or email")

    def clear_password_placeholder(self, event):
        if self.password_entry.get() == "Password":
            self.password_entry.delete(0, tk.END)
            self.password_entry.config(show="*")

    def add_password_placeholder(self, event):
        if not self.password_entry.get():
            self.password_entry.config(show="")
            self.password_entry.insert(0, "Password")

    # API Interaction Handlers
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in [
            "",
            "Phone number, username, or email",
        ] or password in ["", "Password"]:
            messagebox.showwarning(
                "Input Error", "Please fill in both fields."
            )
            return

        try:
            response = requests.post(
                f"{API_URL}/login",
                json={"username": username, "password": password},
            )
            res_data = response.json()

            if response.status_code == 200:
                messagebox.showinfo(
                    "Success",
                    f"{res_data['message']}\nWelcome, {res_data['user']['full_name']}!",
                )
            else:
                messagebox.showerror(
                    "Authentication Failed",
                    res_data.get("message", "Login failed."),
                )
        except requests.exceptions.RequestException:
            messagebox.showerror("Server Error", "Could not connect to API.")

    def handle_forgot_password(self, event=None):
        username = self.username_entry.get()
        if username in ["", "Phone number, username, or email"]:
            messagebox.showwarning(
                "Input Required",
                "Please enter your username/email in the top field first.",
            )
            return

        try:
            response = requests.post(
                f"{API_URL}/forgot-password", json={"identifier": username}
            )
            res_data = response.json()

            if response.status_code == 200:
                messagebox.showinfo("Password Reset", res_data["message"])
            else:
                messagebox.showerror(
                    "Error", res_data.get("message", "User not found.")
                )
        except requests.exceptions.RequestException:
            messagebox.showerror("Server Error", "Could not connect to API.")


# ==========================================
# 3. APPLICATION LAUNCHER
# ==========================================

if __name__ == "__main__":
    # Start Flask API thread in the background
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

    # Brief delay to allow Flask server initialization
    time.sleep(0.5)

    # Launch GUI in main thread
    root = tk.Tk()
    app = InstagramLoginPage(root)
    root.mainloop()
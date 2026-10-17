from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_key_for_secure_sessions"

# Our mock database storing user details
# Format: "username": {"password": "...", "contact": "..."}
users_database = {
    "rudransh": {"password": "password123", "contact": "rudra@example.com"}
}

# ==========================================
# PAGE 1: Welcome & Options (Register / Login / Forgot)
# ==========================================
@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    message_type = "error"  # 'error' or 'success'
    
    if request.method == "POST":
        action_type = request.form.get("action_type")
        
        # --- CREATE NEW ACCOUNT ---
        if action_type == "register":
            username = request.form.get("username").strip()
            contact = request.form.get("contact").strip()
            password = request.form.get("password")
            
            #  Is the username already taken?
            if username in users_database:
                message = "That username is already taken. Please choose another."
            else:
                # Save new user data
                users_database[username] = {"password": password, "contact": contact}
                session["logged_user"] = username  # Log them in automatically
                return redirect(url_for("dashboard"))

        # --- LOG IN ---
        elif action_type == "login":
            username = request.form.get("username").strip()
            password = request.form.get("password")
            
            # Do credentials match?
            if username in users_database and users_database[username]["password"] == password:
                session["logged_user"] = username
                return redirect(url_for("dashboard"))
            else:
                message = "Invalid username or password. Please try again."

        # --- FORGOT PASSWORD ---
        elif action_type == "forgot":
            contact_input = request.form.get("contact").strip()
            found = False
            
            # Search database for contact/email
            for username, data in users_database.items():
                if data["contact"] == contact_input:
                    message = f"Password reset instructions have been sent to {contact_input}!"
                    message_type = "success"
                    found = True
                    break
            
            if not found:
                message = "We couldn't find an account matching that email or contact number."

    return render_template("index.html", message=message, message_type=message_type)


# ==========================================
# PAGE 2: Dashboard / Welcome Page
# ==========================================
@app.route("/dashboard")
def dashboard():
    # If user isn't logged in, block access and send them back to Page 1
    if "logged_user" not in session:
        return redirect(url_for("index"))
    
    username = session["logged_user"]
    return render_template("dashboard.html", username=username)


# ==========================================
# LOGOUT 
# ==========================================
@app.route("/logout")
def logout():
    session.pop("logged_user", None)  # Clear the user session
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
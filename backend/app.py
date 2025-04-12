from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
import json
import os

app = Flask(
    __name__,
    static_folder="../frontend",     
    static_url_path="/static"                   
)

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=2)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("../frontend", filename)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        users = load_users()
        user = users.get(email)

        if user and user["password"] == password:
            return redirect(url_for('serve_static', filename='pages/index.html'))
        else:
            # Vraćanje JSON odgovora umjesto teksta
            return jsonify({"error": "Incorrect email or password!"}), 400

    return redirect(url_for('serve_static', filename='pages/Login.html'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not (fullname and email and password and password == confirm_password):
            return jsonify({"error": "All fields are required and passwords must match!"}), 400

        users = load_users()

        if email in users:
            return jsonify({"error": "User with this email already exists!"}), 400

        users[email] = {
            "fullname": fullname,
            "password": password
        }

        save_users(users)

        return redirect(url_for('serve_static', filename='pages/Login.html'))

    return redirect(url_for('serve_static', filename='pages/Register.html'))


if __name__ == "__main__":
    app.run(debug=True)

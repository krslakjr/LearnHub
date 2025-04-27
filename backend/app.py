from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, session
import json
import os
from flask_cors import CORS

app = Flask(
    __name__,
    static_folder="../frontend",     
    static_url_path="/static"                   
)
app.secret_key = 'tajni_kljuc'
CORS(app, supports_credentials=True)

USERS_FILE = "users.json"
COURSES_FILE = "course_data.json" 

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=2)

def load_courses():
    if os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, "r") as file:
            return json.load(file)
    return []

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("../frontend", filename)

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    users = load_users()
    user = users.get(email)

    if user and user["password"] == password:
        session["user"] = email
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Incorrect email or password!"}), 400

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True})

@app.route("/check-login")
def check_login():
    return jsonify({"logged_in": "user" in session})

@app.route("/course", methods=["GET"])
def get_courses():
    courses = load_courses()
    return jsonify(courses)

@app.route("/course/<path:course_name>", methods=["GET"])
def get_course_by_name(course_name):
    print(f"Received request for course: {course_name}")
    courses = load_courses()
    course = next((course for course in courses if course["name"].lower() == course_name.lower()), None)
    
    if course:
        return jsonify(course)
    else:
        return jsonify({"error": "Course not found!"}), 404


if __name__ == '__main__':
    app.run(debug=True)

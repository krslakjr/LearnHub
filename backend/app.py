from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, session
import json
import os
from flask_cors import CORS
from datetime import datetime

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
        with open(COURSES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_courses(courses):
    with open(COURSES_FILE, "w", encoding="utf-8") as file:
        json.dump(courses, file, indent=2)

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


@app.route("/register", methods=["POST"])
def register_post():
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
    return jsonify({"success": True}), 200

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
        has_quiz = False
        for module in course.get('modules', []):
            for lesson in module.get('lessons', []):
                if lesson.get('quiz'):
                    has_quiz = True
                    break
            if has_quiz:
                break
        course['has_quiz'] = has_quiz
        return jsonify(course)
    else:
        return jsonify({"error": "Course not found!"}), 404

@app.route("/enroll", methods=["POST"])
def enroll():
    if "user" not in session:
        return jsonify({"error": "User not logged in!"}), 400

    email = session["user"]
    course_name = request.json.get("course_name")
    courses = load_courses()

    course = next((course for course in courses if course["name"].lower() == course_name.lower()), None)
    if not course:
        return jsonify({"error": "Course not found!"}), 404

    users = load_users()
    user = users.get(email)
    if user:
        if "enrolled_courses" not in user:
            user["enrolled_courses"] = []
        user["enrolled_courses"].append(course_name)
        save_users(users)
        return jsonify({"success": True, "message": "Enrolled successfully!"}), 200

    return jsonify({"error": "User not found!"}), 404

@app.route("/unenroll", methods=["POST"])
def unenroll():
    if "user" not in session:
        return jsonify({"error": "User not logged in!"}), 400

    email = session["user"]
    course_name = request.json.get("course_name")
    users = load_users()

    user = users.get(email)
    if not user:
        return jsonify({"error": "User not found!"}), 404

    if "enrolled_courses" not in user or course_name not in user["enrolled_courses"]:
        return jsonify({"error": "User is not enrolled in this course!"}), 400

    user["enrolled_courses"].remove(course_name)
    save_users(users)

    courses = load_courses()
    course = next((course for course in courses if course["name"].lower() == course_name.lower()), None)
    if course:
        if "enrolled_students" in course and email in course["enrolled_students"]:
            course["enrolled_students"].remove(email)
        save_courses(courses)
        return jsonify({"success": True, "message": "User unenrolled successfully!"}), 200
    else:
        return jsonify({"error": "Course not found!"}), 404

@app.route('/lesson/<course_name>/<module_title>/<lesson_title>')
def get_lesson(course_name, module_title, lesson_title):
    print(course_name, module_title, lesson_title)
    courses = load_courses()
    course = next((c for c in courses if c["name"].lower() == course_name.lower()), None)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    module = next((m for m in course['modules'] if m['title'].lower() == module_title.lower()), None)
    if not module:
        return jsonify({'error': 'Module not found'}), 404

    lesson = next((l for l in module['lessons'] if l['lesson_title'].lower() == lesson_title.lower()), None)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    return jsonify({
        "lesson_title": lesson['lesson_title'],
        "video_thumbnail": lesson.get('videos', [])[0] if lesson.get('videos') else None,
        "videos": lesson.get('videos', []),
        "instructor": course['teacher']['name'],
        "lesson_description": lesson['description'],
        "lesson_content": lesson['content'],
        "sample_task": lesson.get('sample_task'),
        "quiz":lesson.get('quiz')
    })

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    email = session['user']
    data = request.get_json()
    course_name = data.get('course_name')
    score = data.get('score')
    total_questions = data.get('total_questions')

    if not course_name or score is None or total_questions is None:
        return jsonify({'error': 'Missing quiz submission data'}), 400

    users = load_users()
    user = users.get(email)

    if user:
        if 'quiz_results' not in user:
            user['quiz_results'] = {}
        if course_name not in user['quiz_results']:
            user['quiz_results'][course_name] = []

        user['quiz_results'][course_name].append({
            'timestamp': datetime.utcnow().isoformat(),
            'score': score,
            'total_questions': total_questions
        })
        save_users(users)
        return jsonify({'success': True, 'message': 'Quiz results submitted successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/leaderboard/<course_name>')
def get_leaderboard(course_name):
    users = load_users()
    leaderboard_data = []

    for email, user_data in users.items():
        if 'quiz_results' in user_data and course_name in user_data['quiz_results']:
            results = user_data['quiz_results'][course_name]
            total_score = 0
            total_correct_answers = 0 
            total_questions = 0

            for result in results:
                total_score += result.get('score', 0)
                total_correct_answers += result.get('score', 0)
                total_questions += result.get('total_questions', 0)

            if total_questions > 0:
                leaderboard_data.append({
                    'username': user_data.get('fullname', email.split('@')[0]), 
                    'totalScore': total_score,
                    'correctAnswers': total_correct_answers,
                    'totalQuestions': total_questions
                })
            elif results:
                leaderboard_data.append({
                    'username': user_data.get('fullname', email.split('@')[0]),
                    'totalScore': 0,
                    'correctAnswers': 0,
                    'totalQuestions': 0
                })
        elif 'enrolled_courses' in user_data and course_name in user_data['enrolled_courses']:
            leaderboard_data.append({
                'username': user_data.get('fullname', email.split('@')[0]),
                'totalScore': 0,
                'correctAnswers': 0,
                'totalQuestions': 0
            })

    leaderboard_data.sort(key=lambda x: x['totalScore'], reverse=True)
    return jsonify(leaderboard_data)

if __name__ == '__main__':
    app.run(debug=True)
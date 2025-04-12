from flask import Flask, request, redirect, url_for, send_from_directory

import os

app = Flask(
    __name__,
    static_folder="../frontend",     
    static_url_path=""                   
)

#Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email and password:
            return redirect("/pages/index.html")
        else:
            return "Morate unijeti i email i šifru!"

    return send_from_directory("../frontend/pages", "Login.html")


if __name__ == "__main__":
    app.run(debug=True)

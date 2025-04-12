from flask import Flask, request, redirect, url_for, send_from_directory

app = Flask(
    __name__,
    static_folder="../frontend",     
    static_url_path="/static"                   
)

# Nova ruta za serviranje statičkih fajlova
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("../frontend", filename)

#Login ruta
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email and password:
            return redirect(url_for('serve_static', filename='pages/index.html'))  # Korištenje nove rute
        else:
            return "Morate unijeti i email i šifru!"

    return redirect(url_for('serve_static', filename='pages/Login.html'))  # Korištenje nove rute

#register ruta
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if fullname and email and password and password == confirm_password:
            return redirect(url_for('serve_static', filename='pages/Login.html'))  # Korištenje nove rute
        else:
            return "Sva polja su obavezna i šifre se moraju poklapati!"

    return redirect(url_for('serve_static', filename='pages/Register.html'))  # Korištenje nove rute

if __name__ == "__main__":
    app.run(debug=True)

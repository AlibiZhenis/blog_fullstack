from functools import wraps

import pymysql

pymysql.install_as_MySQLdb()

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "alibi2004"
app.config['MYSQL_DB'] = "blogApp"
app.config['MYSQL_CURSORCLASS'] = "DictCursor"
mysql = MySQL(app)


@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")


@app.route('/post', methods=["GET"])
def blogs():
    return render_template("posts.html")


@app.route('/posts/<id>', methods=["GET"])
def blog(id):
    return render_template("post.html", id=id)


class Register(Form):
    name = StringField("Name", [validators.Length(min=1, max=30)])
    username = StringField("Userame", [validators.Length(min=5, max=30)])
    password = PasswordField("Password", [
        validators.Length(min=8, max=40), validators.DataRequired(),
        validators.equal_to("confirm", message="Passwords must match")
    ])
    confirm = PasswordField("Confirm Password", [validators.Length(min=8, max=40)])


@app.route('/register', methods=["GET", "POST"])
def register():
    form = Register(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, username, password) VALUES(%s, %s, %s)", (name, username, password))

        mysql.connection.commit()
        cur.close()

        flash("Registration is successful! You can now log in.", "success")

        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password_cand = request.form["password"]

        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM users WHERE username =  %s", [username])

        if res > 0:
            data = cur.fetchone()
            password = data["password"]

            if sha256_crypt.verify(password_cand, password):
                session["logged_in"] = True
                session["username"] = username

                flash("Login successful", "success")
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Username or password is incorrect")
        else:
            return render_template("login.html", error="Username or password is incorrect")

        cur.close()

    return render_template("login.html")


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized", "danger")
            return redirect(url_for("login"))

    return wrap


@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logout successful", "success")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET"])
@is_logged_in
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.secret_key = "12345"
    app.run(debug=True)

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


@app.route('/posts', methods=["GET"])
def posts():
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM blogs")
    posts = cur.fetchall()
    cur.close()
    if res > 0:
        return render_template("posts.html", posts=posts)

    return render_template("posts.html", msg='No blog posts yet')


@app.route('/posts/<id>', methods=["GET"])
def post(id):
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM blogs WHERE id=%s", (id))
    post = cur.fetchone()
    cur.close()
    if res > 0:
        return render_template("post.html", post=post)

    return render_template("posts.html", msg='No blog posts yet')


class Register(Form):
    name = StringField("Name", [validators.Length(min=1, max=30)])
    username = StringField("Username", [validators.Length(min=5, max=30)])
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
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM blogs WHERE author=%s", (session["username"]))
    posts = cur.fetchall()
    cur.close()
    if res > 0:
        return render_template("dashboard.html", posts=posts)

    return render_template("dashboard.html", msg="You do not have any blog posts")


class addPost(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField("Body", [validators.Length(min=20), validators.DataRequired()])


@app.route("/add_post", methods=["GET", "POST"])
@is_logged_in
def add_post():
    form = addPost(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blogs(title, author, body) VALUES(%s, %s, %s)", (title, session["username"], body))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("dashboard"))
    return render_template("add_post.html", form=form)


@app.route("/edit_post/<id>", methods=["GET", "POST"])
@is_logged_in
def edit_post(id):
    form = addPost(request.form)

    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()
        res = cur.execute("UPDATE blogs SET title=%s, body=%s WHERE id=%s", (title, body, id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("dashboard"))

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM blogs WHERE id=%s", id)
    post = cur.fetchone()
    if res > 0:
        form.title.data = post["title"]
        form.body.data = post["body"]
    return render_template("edit_post.html", form=form)

@app.route("/delete_post<id>", methods=["POST"])
@is_logged_in
def delete_post(id):

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM blogs WHERE id=%s", id)
    mysql.connection.commit()
    cur.close()

    flash("Post was successfully deleted", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.secret_key = "12345"
    app.run(debug=True)

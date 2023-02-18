from flask import Blueprint, render_template, flash, redirect, request, session
from wtforms import Form, StringField, PasswordField, validators
from api.data import DB
from functools import wraps

authBlueprint = Blueprint('auth', __name__)
db = DB()


class Register(Form):
    name = StringField("Name", [validators.Length(min=1, max=30)])
    username = StringField("Username", [validators.Length(min=5, max=30)])
    password = PasswordField("Password", [
        validators.Length(min=8, max=40), validators.DataRequired(),
        validators.equal_to("confirm", message="Passwords must match")
    ])
    confirm = PasswordField("Confirm Password", [validators.Length(min=8, max=40)])


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized", "danger")
            return redirect("/login")

    return wrap


@authBlueprint.route('/register', methods=["GET", "POST"])
def register():
    form = Register(request.form)
    if request.method == "POST" and form.validate():
        db.create_user(form)
        flash("Registration is successful! You can now log in.", "success")
        return redirect("/login")
    return render_template("register.html", form=form)


@authBlueprint.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        res, verified = db.authenticate(request)
        if res > 0:
            if verified:
                flash("Login successful", "success")
                return redirect("/dashboard")
            else:
                return render_template("login.html", error="Username or password is incorrect")
        else:
            return render_template("login.html", error="Username or password is incorrect")

    return render_template("login.html")


@authBlueprint.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logout successful", "success")
    return redirect("/login")

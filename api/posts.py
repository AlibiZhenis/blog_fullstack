from flask import Blueprint, render_template, flash, redirect, request
from api.data import DB
from wtforms import Form, StringField, TextAreaField, validators
from api.auth import is_logged_in

postsBlueprint = Blueprint('posts', __name__)
db = DB()


@postsBlueprint.route('/', methods=["GET"])
def index():
    return render_template("index.html")


@postsBlueprint.route('/posts', methods=["GET"])
def posts():
    res, objs = db.get_all_posts()
    if res > 0:
        return render_template("posts.html", posts=objs)
    return render_template("posts.html", msg='No blog posts yet')


@postsBlueprint.route('/posts/<id>', methods=["GET"])
def post(id):
    res, obj = db.get_post_id(id)
    if res > 0:
        return render_template("post.html", post=obj)
    return render_template("posts.html", msg='No blog posts yet')


class addPost(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField("Body", [validators.Length(min=20), validators.DataRequired()])


@postsBlueprint.route("/add_post", methods=["GET", "POST"])
@is_logged_in
def add_post():
    form = addPost(request.form)
    if request.method == "POST" and form.validate():
        db.create_post(form)
        return redirect("/dashboard")
    return render_template("add_post.html", form=form)


@postsBlueprint.route("/edit_post/<id>", methods=["GET", "POST"])
@is_logged_in
def edit_post(id):
    form = addPost(request.form)

    if request.method == "POST" and form.validate():
        db.update_post(form, id)
        return redirect("/dashboard")

    res, post = db.get_post_id(id)
    if res > 0:
        form.title.data = post["title"]
        form.body.data = post["body"]
    return render_template("edit_post.html", form=form)


@postsBlueprint.route("/delete_post/<id>", methods=["POST"])
@is_logged_in
def delete_post(id):
    db.delete_post(id)
    flash("Post was successfully deleted", "success")
    return redirect("/dashboard")


@postsBlueprint.route("/dashboard", methods=["GET"])
@is_logged_in
def dashboard():
    res, objs = db.get_posts_by_username()
    if res > 0:
        return render_template("dashboard.html", posts=objs)
    return render_template("dashboard.html", msg="You do not have any blog posts")

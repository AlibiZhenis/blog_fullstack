import pymysql

pymysql.install_as_MySQLdb()

from flask import Flask, session
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "alibi2004"
app.config['MYSQL_DB'] = "blogApp"
app.config['MYSQL_CURSORCLASS'] = "DictCursor"
mysql = MySQL(app)

class DB():

    mysql = mysql

    def get_all_posts(self):
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM blogs")
        posts = cur.fetchall()
        cur.close()
        return res, posts

    def get_post_id(self, id):
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM blogs WHERE id=%s", id)
        post = cur.fetchone()
        cur.close()
        return res, post

    def create_post(self, form):
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blogs(title, author, body) VALUES(%s, %s, %s)", (title, session["username"], body))
        mysql.connection.commit()
        cur.close()

    def update_post(self, form, id):
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()
        cur.execute("UPDATE blogs SET title=%s, body=%s WHERE id=%s", (title, body, id))
        mysql.connection.commit()
        cur.close()

    def delete_post(self, id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM blogs WHERE id=%s", id)
        mysql.connection.commit()
        cur.close()

    def get_posts_by_username(self):
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM blogs WHERE author=%s", session["username"])
        posts = cur.fetchall()
        cur.close()
        return res, posts

    def create_user(self, form):
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, username, password) VALUES(%s, %s, %s)", (name, username, password))

        mysql.connection.commit()
        cur.close()

    def authenticate(self, request):
        username = request.form["username"]
        password_cand = request.form["password"]

        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM users WHERE username =  %s", [username])

        if res > 0:
            data = cur.fetchone()
            cur.close()
            password = data["password"]

            if sha256_crypt.verify(password_cand, password):
                session["logged_in"] = True
                session["username"] = username
                return res, True
            else:
                return res, False
        else:
            cur.close()
            return 0, False


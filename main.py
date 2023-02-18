from api.auth import authBlueprint
from api.posts import postsBlueprint
from api.data import app

app.register_blueprint(authBlueprint)
app.register_blueprint(postsBlueprint)

if __name__ == "__main__":
    app.secret_key = "12345"
    app.run(debug=True)

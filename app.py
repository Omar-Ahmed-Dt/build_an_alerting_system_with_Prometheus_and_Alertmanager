from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware  # Add this line

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

@app.route("/")
@app.route("/up")
def up():
    return "I am running!"

if __name__ == "__main__":
    app.run(debug=True)
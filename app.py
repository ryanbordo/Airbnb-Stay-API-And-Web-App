from flask import Flask
from flask import url_for
from views import views

app = Flask(__name__,
            static_url_path='', 
            static_folder='static')
app.register_blueprint(views, url_prefix = "/")

@app.route("/favicon.ico")
def favicon():
    return url_for('static', filename='data:,')

if  __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug=True)
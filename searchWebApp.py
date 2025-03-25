from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['ENV'] = "Development"
app.config['DEBUG'] = True

@app.route('/')
def searchHome():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)

from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['ENV'] = "Development"
app.config['DEBUG'] = True


@app.route('/')
def searchHome():
    return render_template('search.html')


#Result Landing Page Function
@app.route('/getResult', methods=['POST'])
def getResult():
    resultOutput = '''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Result</title>
                <!--Bootstrap Framework CDN-->
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
                    integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
                    integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
            </head>
            <body>
                <div class="card">
                    <div class="card-body">
                        <h1 class="card-title">Results</h1>
                        <h2 class="card-subtitle">I have no clue!</h2>
                        <a href="/" class="btn btn-primary">Back to Search</a>
                    </div>
                </div>
            </body>
        </html>'''
    return resultOutput



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)

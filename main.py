'''

This application shortens URLs

'''
import secrets
import re
from pathlib import Path
from flask import Flask, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy

PATH_LOCATION = Path(__file__).absolute().parent
DOMAIN = '127.0.0.1:5000'

# Creates the flask application and sets up the database
app = Flask(__name__, instance_path=PATH_LOCATION)
app.secret_key = 'YOUR KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class urls(db.Model):
    _id = db.Column('id', db.Integer, primary_key=True)
    url = db.Column(db.String(100))
    short_url = db.Column(db.String(100))

    def __init__(self, url, short_url):
        self.url = url
        self.short_url = short_url

def url_validator(url):
    regex = re.compile(r'https?://(?:www\.)?[a-zA-Z0-9./]+')
    return bool(regex.match(url))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        random_key = secrets.token_urlsafe(4)
        key_exists = urls.query.filter_by(short_url=random_key).first()
        valid = url_validator(original_url)

        # Checks if key has been repeated
        while key_exists:
            random_key = secrets.token_urlsafe(4)
            key_exists = urls.query.filter_by(short_url=random_key).first()

        # Reloads page if url is invalid
        if not valid:
            return redirect(request.url)

        # Checks if url has already been shortened before
        url_query = urls.query.filter_by(url=original_url).first()
        if url_query:
            generated_url = url_query
        else:
            generated_url = urls(original_url, random_key)
            db.session.add(generated_url)
            db.session.commit()
        
        full_short_url = f'{DOMAIN}/{generated_url.short_url}'
        
        return render_template('index.html', short_url=full_short_url)

    return render_template('index.html')

@app.route('/<short_url>')
def short(short_url):
    url_query = urls.query.filter_by(short_url=short_url).first()

    if url_query:
        url = url_query.url
        return redirect(url)
    else:
        abort(404)

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()

    app.run(debug=True)
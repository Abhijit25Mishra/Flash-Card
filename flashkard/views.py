from flask import Blueprint, render_template, request, flash
from flask.helpers import send_file
from flask_login import login_user, logout_user, current_user
from flask_login.utils import login_required
from werkzeug.utils import redirect
from .models import User, Deck, Card
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
import os
import csv
import time

views = Blueprint("views", __name__)

BASE = 'http://127.0.0.1:5000'


@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def home():
    data = requests.get(BASE+f'/api/deck/{current_user.username}')
    return render_template('dashboard.html', decks=data.json(), user=current_user.username)


@views.route('/', methods=['GET'])
def landing():
    return render_template('landing.html')


@views.route('/review/<string:deck>', methods=['GET', 'POST'])
@login_required
def review(deck):
    t = datetime.now()
    d = Deck.query.filter_by(deck_name=deck).first()
    d.last_rev = t
    db.session.commit()
    data = requests.get(BASE + f'/api/{current_user.username}/{deck}/card')

    if data:
        return render_template('review.html', front=data.json()['front'], back=data.json()['back'], deck=data.json()['deck'], card_id=data.json()['card_id'])
    else:
        return render_template('review.html', deck=deck, data=True)


@views.route('/review/<string:deck>/<int:card_id>', methods=['GET', 'POST'])
def score(deck, card_id):
    if request.method == 'POST':
        c = Card.query.filter_by(card_id=card_id).first()
        s = int(request.form.get('score'))
        c.score = s
        db.session.commit()
        d = Deck.query.filter_by(
            deck_name=deck, user=current_user.username).first()
        cn = Card.query.filter_by(deck=deck).count()
        d.score = d.score + (c.score/cn)
        db.session.commit()
        return redirect(f'/review/{deck}')


@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect('/dashboard')
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template('login.html')


@views.route('/register', methods=['GET', 'POST'])
def register():

    return render_template('register.html')


@views.route('/<string:user>/deck/<string:deck>/delete', methods=['GET', 'POST'])
def deletedeck(deck, user):
    d = Deck.query.filter_by(deck_name=deck, user=user).first()
    db.session.delete(d)
    db.session.commit()
    return redirect('/dashboard')


def isallowed(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.lower() == 'csv':
        return True
    else:
        return False


@views.route('/fileupload', methods=['GET', 'POST'])
def fileupload():
    if request.method == "POST":
        if request.files:
            csvfile = request.files['csvfile']
            print(csvfile)
            if isallowed(csvfile.filename):
                csvfile.save(os.path.join(
                    'C:\\Users\\ASUS\\OneDrive\\Desktop\\MAD\\capstone\\flashkard\\static\\', csvfile.filename))
                d = Deck(deck_name=csvfile.filename.split(
                    '.')[0], user=current_user.username)
                db.session.add(d)
                db.session.commit()
                with open(f'C:\\Users\\ASUS\\OneDrive\\Desktop\\MAD\\capstone\\flashkard\\static\\{csvfile.filename}', 'r') as f:
                    c = csv.reader(f)
                    next(c)
                    for i in c:
                        print(i)
                        c = Card(front=i[1], back=i[2],
                                 deck=csvfile.filename.split('.')[0])
                        db.session.add(c)
                        db.session.commit()

                return redirect('/dashboard')
            else:
                flash('Only CSV files are allowed')
                return redirect('/dashboard')


@views.route('/export/<string:deck>', methods=['GET', 'POST'])
def export(deck):
    c = Card.query.filter_by(deck=deck)
    i = 1
    with open(f'{deck}.csv', 'w', encoding="utf-8") as f:
        w = csv.writer(f)
        for card in c:
            w.writerow([i, card.front, card.back])
            i = i+1
    time.sleep(2)
    return send_file(f'C:\\Users\\ASUS\\OneDrive\\Desktop\\MAD\\capstone\{deck}.csv', as_attachment=True)


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

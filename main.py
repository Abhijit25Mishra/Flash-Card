from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '21f1003261'


# Check session for each end point except allowed routes
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

# Login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    # retrieve username and password from form
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # connect to database
        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        query = """SELECT * FROM users WHERE username=? AND password=?"""
        cur.execute(query, (username, password))
        rows = cur.fetchall()

        # if username and password match, log user in else redirect to signup page

        if len(rows) == 1:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return redirect(url_for('signup'))
    return render_template('login.html')

# signup page


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == "POST":
        # error handling
        try:
            # retrieve username and password from form
            name = request.form['name']
            username = request.form['username']
            password = request.form['password']
            # connect to database
            conn = sqlite3.connect("project.db")
            cur = conn.cursor()
            query = """INSERT INTO users (name,username,password) VALUES (?,?,?)"""
            cur.execute(query, (name, username, password))
            conn.commit()
            # check if username already exists
            if cur.rowcount == 1:
                return "signup successfully <a href='/login'>Go to Login</a>"
            else:
                return "Username already exists <a href='/signup'>Try again</a>"
        except:
            return "Something wrong"

    return render_template('signup.html')

# index page (Dashboard)


@app.route('/')
def index():
    conn = sqlite3.connect("project.db")
    cur = conn.cursor()
    query = """SELECT deckname from cards WHERE front IS NULL"""
    cur.execute(query)
    rows = cur.fetchall()
    return render_template('index.html', rows=rows)

# add card page


@app.route('/createdeck', methods=['GET', 'POST'])
def createdeck():
    if request.method == "POST":
        deckname = request.form['deckname']
        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        query = """INSERT INTO cards (deckname) VALUES (?)"""
        cur.execute(query, (deckname,))
        conn.commit()
        return redirect(url_for('index'))
    return render_template('createdeck.html')

# Delete deck


@app.route('/deletedeck/<deckname>')
def deletedeck(deckname):
    conn = sqlite3.connect("project.db")
    cur = conn.cursor()
    query = """DELETE FROM cards WHERE deckname=?"""
    cur.execute(query, (deckname,))
    conn.commit()
    return redirect(url_for('index'))

# update deck page


@app.route('/updatedeck/<deckname>', methods=['GET', 'POST'])
def updatedeck(deckname):
    if request.method == "POST":
        old = deckname
        new = request.form['new']
        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        query = """UPDATE cards SET deckname=? WHERE deckname=?"""
        cur.execute(query, (new, old))
        conn.commit()
        return redirect(url_for('index'))
    return render_template('updatedeck.html', deckname=deckname)

# review page


@app.route('/review/<deckname>')
def review(deckname):

    conn = sqlite3.connect("project.db")
    cur = conn.cursor()
    query = """SELECT * FROM cards WHERE deckname=? AND front IS NOT NULL ORDER BY RANDOM() LIMIT 1"""
    #query="""SELECT * FROM cards WHERE deckname=? AND front IS NOT NULL"""
    cur.execute(query, (deckname,))
    rows = cur.fetchone()
    if rows is not None:
        return render_template('review.html', deckname=deckname, rows=rows)
    else:
        return redirect(url_for('index'))

# add card page


@app.route('/addcard/<deckname>', methods=['GET', 'POST'])
def addcard(deckname):
    if request.method == "POST":
        front = request.form['front']
        back = request.form['back']

        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        query = """INSERT INTO cards (deckname,front,back) VALUES (?,?,?)"""
        cur.execute(query, (deckname, front, back))
        conn.commit()
        return redirect(url_for('index'))
    return render_template('addcard.html', deckname=deckname)


if __name__ == "__main__":
    app.run(debug=True)

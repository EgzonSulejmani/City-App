from flask import Flask, render_template, url_for, request, flash, session, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import os
from validators import *

app = Flask(__name__)


# sessions
app.secret_key = "21flask_42342_sqlalchemy404"

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:/// firstapp.db'
db = SQLAlchemy(app)

# bcrypt
bcrypt = Bcrypt(app)

# upload
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/photos/')
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User %s>" % self.email


class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    adress = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, user_id, adress):
        self.title = title
        self.user_id = user_id
        self.adress = adress

    def __repr__(self):
        return "<Market %s>" % self.title


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, user_id):
        self.title = title
        self.user_id = user_id

    def __repr__(self):
        return "<Album %s>" % self.title


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.String(120), nullable=False)
    album_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, photo, album_id):
        self.title = title
        self.photo = photo
        self.album_id = album_id

    def __repr__(self):
        return "<Photo %s>" % self.title


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=True, nullable=False)
    adress = db.Column(db.String(60), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, user_id, adress):
        self.title = title
        self.user_id = user_id
        self.adress = adress

    def __repr__(self):
        return "<Store %s>" % self.title


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=True, nullable=False)
    adress = db.Column(db.String(60), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, user_id, adress):
        self.title = title
        self.user_id = user_id
        self.adress = adress

    def __repr__(self):
        return "<Hospital %s>" % self.title


class GasStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=True, nullable=False)
    adress = db.Column(db.String(60), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, user_id, adress):
        self.title = title
        self.user_id = user_id
        self.adress = adress

    def __repr__(self):
        return "<GasStation %s>" % self.title


@app.route("/")
def homepage():
    return render_template('home.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if not_empty([email, password]):
            if is_email(email):
                user = User.query.filter_by(email=email).first()
                if user:
                    if bcrypt.check_password_hash(user.password, password):

                        session['is_logged_in'] = True
                        session['username'] = user.username
                        session['user_id'] = user.id
                        session['email'] = email
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Password is incorrect!")
                else:
                    flash("User doesn't exist!")
            else:
                flash("Email is not valid!")
        else:
            flash("All fields are required!")
        return redirect(url_for("login"))
    else:
        if session['is_logged_in'] == True:
            return redirect(url_for('dashboard'))
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not_empty([username, email, password]):
            if is_email(email):
                if password_match(password):
                    password_hash = bcrypt.generate_password_hash(password)
                    user = User(username, email, password_hash)
                    db.session.add(user)
                    db.session.commit()
                    session['is_logged_in'] = True
                    session['username'] = username
                    session['email'] = email
                    return redirect(url_for("dashboard"))
                else:
                    flash("Pass doesnt match")
            else:
                flash("Email is not valid")
        else:
            flash("All fields are required!")
        return redirect(url_for('register'))
    else:
        if session['is_logged_in'] == True:
            return redirect(url_for('dashboard'))
        return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if session['is_logged_in'] == False:
        return '''
            <p>You are not allowed to view this page without authorization!</p>
            <a href="/login">Login</a>
        '''
    return render_template("dashboard.html")


@app.route("/kumanova")
def kumanova():
    return render_template("kumanova.html")


@app.route("/market", methods=["GET", "POST"])
def market():
    if session['is_logged_in'] == True:
        market = Market.query.all()
        if request.method == "POST":
            adress = request.form['adress']
            title = request.form['title']

            if not_empty([title, adress]):
                markets = Market(title, adress, session.get('user_id'))
                db.session.add(markets)
                db.session.commit()
                flash("Market created successfully")
                return redirect(url_for('market'))
        return render_template("market.html", market=market)
    else:
        return redirect(url_for("login"))


@app.route("/albums", methods=["GET", "POST"])
def albums():
    if session['is_logged_in'] == True:
        albums = Album.query.all()
        if request.method == "POST":
            title = request.form['title']
            album = Album(title, session.get('user_id'))
            db.session.add(album)
            db.session.commit()
            flash("Album created")
            return redirect(url_for('albums'))
        return render_template("albums.html", albums=albums)
    else:
        return redirect(url_for('homepage'))


@app.route("/album/<int:album_id>/delete")
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    flash("Album was deleted successfully")
    return redirect(url_for('albums'))


@app.route("/photos/<int:album_id>", methods=["GET", "POST"])
def photos(album_id):
    if session['is_logged_in'] == True:
        album = Album.query.get_or_404(album_id)
        photos = Photo.query.filter_by(album_id=album.id).all()
        if request.method == "POST":
            title = request.form['title']
            file = request.files['photo']

            if file and allowed_file(file.filename):

                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                photo = Photo(title, file.filename, album_id)
                db.session.add(photo)
                db.session.commit()
                return redirect(url_for('photos', album_id=album_id))
        return render_template("photos.html", photos=photos, album=album)
    else:
        return redirect(url_for("homepage"))


@app.route("/markets/<int:markets_id>/delete")
def delete_markets(markets_id):
    markets = Market.query.get_or_404(markets_id)
    db.session.delete(markets)
    db.session.commit()
    flash("Market was deleted")
    return redirect(url_for('market'))


@app.route("/album/<int:album_id>/photo/<int:photo_id>")
def delete_photo(album_id, photo_id):
    photo = Photo.query.get_or_404(photo_id)
    db.session.delete(photo)
    db.session.commit()
    flash("Photo was deleted successfully")
    return redirect(url_for('photos', album_id=album_id))


# @app.route("/set-cookie")
# def setCookie():
#     expire = 60*60*24*30
#     res = make_response(render_template("cookie.html"))
#     res.set_cookie("email", "egzon.sulejmani97@hotmail.com", expire)
#     return res


# @app.route("/get-cookie")
# def getCookie():
#     if request.cookies.get("email") == None:
#         return redirect(url_for('homepage'))
#     return request.cookies.get("email")

@app.route("/search", methods=["POST"])
def search():
    templs = ["market.html"]
    if request.method == "POST":
        title = request.form['search']
        search = "%{}%".format(title)
        market = Market.query.filter(Market.title.like(search)).all()
        return render_template(templs, market=market)


@app.route("/logout")
def logout():
    session['username'] = ""
    session['email'] = ""
    session['is_logged_in'] = False
    return redirect(url_for('homepage'))


def not_empty(form_fields):
    for field in form_fields:
        if len(field) == 0:
            return False
    return True


def is_email(email):
    return re.search("[\w\.\_\-]\@[\w\-]+\.[a-z]{2,5}", email) != None


def password_match(password):
    return password


if __name__ == '__main__':
    app.run(debug=True)

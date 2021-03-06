from flask import Flask, render_template, flash, url_for, redirect, request, session, make_response, send_file, send_from_directory
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import os
from functools import wraps
from content_management import Content
from db_connect import connection
from search import search

APP_CONTENT = Content()

UPLOAD_FOLDER = "/var/www/FlaskApp/FlaskApp/uploads"
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif'])

app = Flask(__name__, instance_path='/var/www/FlaskApp/FlaskApp/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login.")
            return redirect(url_for('login_page'))
    return wrap

#upload file checker: "NEVER TRUST USER INPUT"
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET","POST"])
def main():
    return render_template("main.html")


@app.route("/dashboard/", methods=["GET","POST"])
@login_required
def dashboard():
        flash("This is a flash notification!!!")
        return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)
    
@app.route('/introduction-to-app/', methods=['GET'])
@login_required
def intro_to_app():
    try:
        output = ['Will you ever run out of muffins?',"Non, because I work at ze muffin factory","Wow - Owen Wilson","<p><strong>Hello World!</strong></p>", 42, '42']
        return render_template("templating_demo.html", output = output)
    
    except Exception as e:
        return(str(e))
    
    
    
@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ""
    try:
        c, conn = connection()
        if request.method == "POST":
            data = c.execute("SELECT * FROM users WHERE username  =('{0}')".format(thwart(request.form["username"])))

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form["password"],data):
                session["logged_in"] = True
                session["username"] = request.form["username"]

                flash("You are now logged in!")
                return redirect(url_for("dashboard"))
            else: 
                error = "Invalid credentials, try again"

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        flash(e)
        error = "Invalid credentials, try again"
        return render_template("login.html", error = error)

    
@app.route('/uploads/', methods=["GET","POST"])
@login_required
def upload_file():
    try:
        if request.method == "POST":
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(requrest.url())
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File upload successful')
                return render_template('uploads.html', filename = filename)
        return render_template('uploads.html')
    except:
        flash("Please upload a valid file")
        return render_template('uploads.html"')
    
@app.route('/download/')
@login_required
def download():
    try:
        return send_file('/var/www/FlaskApp/FlaskApp/uploads/goodboy.jpg', attachment_filename='goodboy.jpg')
    except Exception as e:
        return str(r)

    
@app.route('/downloader/', methods=['GET', 'POST'])
@login_required
def downloader():
    error = ''
    try: 
        if request.method =="POST":
            filename = request.form['filename']
            return send_file('/var/www/FlaskApp/FlaskApp/uploads/' + filename, attacment_filename = 'download')
        else:
            return render_template('downloader.html', error = error)
        error = "Please enter a valid file name"
        return render_template('downloader.html', error = error)
    except:
        error = "Please enter a valid file name"
        return render_template("downloader.html", error = error)
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('main'))
    
    
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice', [validators.Required()])

@app.route('/about/', methods=["GET","POST"])
def about_page():
    return render_template('about.html')


@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another.")
                return render_template('register.html', form = form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username), thwart(password), thwart(email), thwart("/dashboard/")))

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form = form)

    except Exception as e:
        return(str(e))

    
@app.route('/search/',methods=["GET","POST"])
def search_site():
    try:
        fuck = ''
        if request.method=="POST":
            stuff = request.form['search']
            fuck = search(stuff+"minimalist")
            return render_template("searchshit.html", fuck = fuck,  APP_CONTENT = APP_CONTENT)
        return render_template("searchshit.html", fuck = fuck,  APP_CONTENT = APP_CONTENT)

    except Exception as e:
        return str(e)
    
@app.route('/sitemap.xml/', methods=['GET'])
def sitemap():
    try:
        pages = []
        week = (datetime.now() - timedelta(days = 7)).date().isoformat()
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments)==0:
                pages.append(
                    ["http://104.131.173.185"+str(rule.rule),week]
                )
        sitemap_xml = render_template('sitemap_template.xml', pages = pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    except Exception as e:
        return(str(e))


@app.route('/robots.txt/')
def robots():
    return("User-agent: *\nDisallow: /register\nDisallow: /login/")
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")



@app.errorhandler(500)
def int_server_error(e):
    return render_template("500.html", error = e)
    


    

if __name__ == "__main__":
	app.run()



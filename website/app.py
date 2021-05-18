import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash

from datetime import timedelta

app = Flask(__name__)
app.secret_key = open("keys/my_key.key", "rb").read()
app.permanent_session_lifetime = timedelta(hours=24)


def emailValid():
    my_db = mysql.connector.connect(
        host="localhost", user="root", passwd="karthi@0709", database="KarthikDB")
    email = request.form['em']

    my_cursor = my_db.cursor(buffered=True)

    sql_code = "SELECT * FROM karthikdb.sign_up_info where email=%(email)s"

    result = my_cursor.execute(sql_code, {'email': email})
    cnt = my_cursor.rowcount
    my_cursor.close()
    my_db.close()
    return cnt == 0


@app.route('/login-register', methods=['GET'])
def index():
    if "name" in session:
        name = session["name"]
        flash("You are already logged in!")
        return redirect(url_for("home"))
    return render_template('index.html')


@app.route('/login-register', methods=['POST'])
def main_register():
    username = request.form['u']
    email = request.form['em']
    password = request.form['pa']
    session["name"] = username
    session["email"] = email
    if request.method == 'POST':
        if not emailValid():
            flash("This User already exists. Please login or sign up as a new user.")
            session.pop("name")
            return redirect(url_for("main_register"))
            # flash("hi", "info")
        if int(len(username)) != 0:
            if int(len(email)) != 0:
                if int(len(password)) != 0:
                    my_database = mysql.connector.connect(host="localhost", user="root", passwd="karthi@0709",
                                                          database="karthikDB")
                    curser = my_database.cursor()

                    sql_form = "Insert into sign_up_info(username, email, passwd) values(%s, %s, %s)"
                    user_ADD = [(username, email, password)]

                    curser.executemany(sql_form, user_ADD)
                    my_database.commit()

                    my_database.close()
                    flash("Sign Up Successful!")
                    return render_template('home.html', name=session["name"])
    flash("Cannot Register with no details!")
    return redirect(url_for("main_register"))


@app.route('/login', methods=['POST'])
def login():
    if "name" in session:
        name = session["name"]
        return redirect(url_for("home"))
    my_db = mysql.connector.connect(
        host="localhost", user="root", passwd="karthi@0709", database="KarthikDB")
    session.permanent = True
    # my_curser = my_db.cursor()
    name = request.form["username"]
    # email = request.form['em']
    pwd = request.form["passwd"]
    my_cursor = my_db.cursor(buffered=True)

    sql_code = "SELECT * FROM karthikdb.sign_up_info where username=%(user_name)s and passwd=%(password)s"
    result = my_cursor.execute(sql_code, {'user_name': name, 'password': pwd})

    cnt = my_cursor.rowcount
    email = ""
    if cnt > 0:
        res = my_cursor.fetchone()
        email = res[2]

    my_cursor.close()
    my_db.close()

    if cnt > 0:

        session["email"] = email
        session["name"] = name
        session["pwd"] = pwd
        if "name" in session:
            name = session["name"]
            flash("Login Successful!")
            return redirect(url_for("home"))
        else:
            return render_template("my_home.html")

    else:
        flash("Invalid username or password!")
        return redirect(url_for("main_register"))


@app.route('/home')
def home():
    if "name" in session:
        name = session['name']
        return render_template('home.html', name=name)
    else:
        return render_template("my_home.html")


@app.route('/logout')
def logout():
    session.pop("name", None)
    session.pop("pwd", None)
    session.clear()
    flash(" You have been logged out")
    return redirect(url_for('main_register'))


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/details', methods=['POST', 'GET'])
def account():
    my_database = mysql.connector.connect(host="localhost", user="root", passwd="karthi@0709",
                                          database="karthikDB")
    curser = my_database.cursor()
    if request.method == 'POST':
        passwd = request.form["pass"]
        c_passwd = request.form["c_pass"]
        session["passw"] = passwd
        
        if len(passwd) != 0 and len(c_passwd) != 0 and len(request.form["o_pass"]) != 0:
            if passwd == c_passwd:
                if request.form["o_pass"] == session["pwd"]:
                    query = "UPDATE karthikdb.sign_up_info SET passwd=%(passwd)s WHERE email=%(email)s"

                    curser.execute(
                        query, {'passwd': session["passw"], 'email': session["email"]})
                    session["pwd"] = session["passw"]
                    my_database.commit()
                    flash("Password Saved")
                    return redirect(url_for("home"))
        if passwd != c_passwd:
            flash("Password not matching")
            return redirect(url_for("home"))
        if request.form["o_pass"] != session["pwd"]:
            flash("Old Password Incorrect")
            return redirect(url_for("home"))
        
    if "name" in session:
        return render_template("account.html", username=session["name"], email=session["email"])
    else:
        flash("Please Login to view the Account details")
        return redirect(url_for("main_register"))


if __name__ == "__main__":
    app.run(debug=True, port=1000, host='0.0.0.0')

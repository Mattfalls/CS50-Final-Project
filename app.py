import os
import json
from random import randint, randrange
import uuid as uuid

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#index.html
@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username[0]["username"]

    pp = db.execute("SELECT profile_pic_test FROM users WHERE id = ?", session["user_id"])
    p2 = db.execute("SELECT p2 FROM users WHERE id = ?", session["user_id"])
    p3 = db.execute("SELECT p3 FROM users WHERE id = ?", session["user_id"])
    p4 = db.execute("SELECT p4 FROM users WHERE id = ?", session["user_id"])
    p5 = db.execute("SELECT p5 FROM users WHERE id = ?", session["user_id"])
    p6 = db.execute("SELECT p6 FROM users WHERE id = ?", session["user_id"])
    pp = pp[0]["profile_pic_test"]
    p2 = p2[0]["p2"]
    p3 = p3[0]["p3"]
    p4 = p4[0]["p4"]
    p5 = p5[0]["p5"]
    p6 = p6[0]["p6"]

    h1 = db.execute("SELECT h1 FROM users WHERE id = ?", session["user_id"])
    h2 = db.execute("SELECT h2 FROM users WHERE id = ?", session["user_id"])
    h3 = db.execute("SELECT h3 FROM users WHERE id = ?", session["user_id"])
    h4 = db.execute("SELECT h4 FROM users WHERE id = ?", session["user_id"])
    h5 = db.execute("SELECT h5 FROM users WHERE id = ?", session["user_id"])
    h6 = db.execute("SELECT h6 FROM users WHERE id = ?", session["user_id"])
    h1 = h1[0]["h1"]
    h2 = h2[0]["h2"]
    h3 = h3[0]["h3"]
    h4 = h4[0]["h4"]
    h5 = h5[0]["h5"]
    h6 = h6[0]["h6"]
    home = [h1, h2, h3, h4, h5, h6]

    already_liked = db.execute("SELECT other_user_id FROM likes WHERE username = ?", username)
    already_liked_user_ids = []
    for i in already_liked:
        already_liked_user_ids.append(i['other_user_id'])

    #display new users / don't display users already liked
    users = db.execute("SELECT * FROM users")
    num_users = len(users)
    randNum = randrange(0, num_users)
    randUser = users[randNum]
    randUsername = randUser["username"]
    randID = randUser["id"]

    randh1 = randUser["h1"]
    randh2 = randUser["h2"]
    randh3 = randUser["h3"]
    randh4 = randUser["h4"]
    randh5 = randUser["h5"]
    randh6 = randUser["h6"]
    bio = randUser["bio"]

    print("\nBEFORE randUsername: ", randUsername)
    print("BEFORE randID: ", randID)
    print("BEFORE Already Liked List: ", already_liked_user_ids, "\n")
    max_tries = num_users * 10

    while True:
        if randID == session["user_id"] or randID in already_liked_user_ids:
            randNum = randrange(0, num_users)  
            randUser = users[randNum]
            randUsername = randUser["username"]
            randID = randUser["id"]
            bio = randUser["bio"]
            randh1 = randUser["h1"]
            randh2 = randUser["h2"]
            randh3 = randUser["h3"]
            randh4 = randUser["h4"]
            randh5 = randUser["h5"]
            randh6 = randUser["h6"]
            max_tries = max_tries - 1
            if max_tries == 0:
                return render_template("no_more_users.html", pp=pp, username=username)
        else:
            break

    print("\nrandUser: ", randUser)
    print("\nrandUsername: ", randUsername)
    print("randID: ", randID)
    print("Already Liked List: ", already_liked_user_ids, "\n")

    #like/dislike mechanism
    like = request.form.get('like')
    dislike = request.form.get('dislike')

    if request.method == "GET":
        return render_template("index.html", bio=bio, randUsername=randUsername, randID=randID, randh1=randh1, randh2=randh2, randh3=randh3, randh4=randh4, randh5=randh5, randh6=randh6, randUser=randUser, randNum=randNum, num_users=num_users, users=users, username=username, pp=pp, home=home)
    else:
        if like:
            like = int(like)
            db.execute("INSERT INTO likes (user_id, username, other_username, other_user_id, like) VALUES (?, ?, ?, ?, 'yes')", session["user_id"], username, users[like - 1]['username'], like)

        elif dislike:
            dislike = int(dislike)
            db.execute("INSERT INTO likes (user_id, username, other_username, other_user_id, like) VALUES (?, ?, ?, ?, 'no')", session["user_id"], username, users[dislike - 1]['username'], dislike)
        return redirect("/")


@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    #share messages
    if request.method == "POST":
        todo = 0
    else:
        return render_template("messages.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    #Retrieve pics, retrieve info, set variables
    pp = db.execute("SELECT profile_pic_test FROM users WHERE id = ?", session["user_id"])
    p2 = db.execute("SELECT p2 FROM users WHERE id = ?", session["user_id"])
    p3 = db.execute("SELECT p3 FROM users WHERE id = ?", session["user_id"])
    p4 = db.execute("SELECT p4 FROM users WHERE id = ?", session["user_id"])
    p5 = db.execute("SELECT p5 FROM users WHERE id = ?", session["user_id"])
    p6 = db.execute("SELECT p6 FROM users WHERE id = ?", session["user_id"])
    pp = pp[0]["profile_pic_test"]
    p2 = p2[0]["p2"]
    p3 = p3[0]["p3"]
    p4 = p4[0]["p4"]
    p5 = p5[0]["p5"]
    p6 = p6[0]["p6"]
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username[0]["username"]
    users = db.execute('SELECT * FROM users WHERE id = ?', session["user_id"])
    gender = db.execute("SELECT gender FROM users WHERE id = ?", session["user_id"])
    gender_pref = db.execute("SELECT gender_comfort FROM users WHERE id = ?", session["user_id"])
    pets_test = db.execute("SELECT pets_test FROM users WHERE id = ?", session["user_id"])
    distance_pref = db.execute("SELECT distance_pref FROM users WHERE id = ?", session["user_id"])
    bio = db.execute("SELECT bio FROM users WHERE id = ?", session["user_id"])

    if request.method == "GET":
        return render_template("profile.html", username=username, pp=pp, p2=p2, p3=p3, p4=p4, p5=p5, p6=p6, users=users, gender=gender, gender_pref=gender_pref, pets_test=pets_test, distance_pref=distance_pref, bio=bio)
    elif request.method == "POST":
        #grab uploaded pics from HTML
        pp = request.form.get("profile_pic")
        if (pp):
            db.execute("UPDATE users SET profile_pic_test = ? WHERE id = ?", pp, session["user_id"])
        p2 = request.form.get("pic2")
        if (p2):
            db.execute("UPDATE users SET p2 = ? WHERE id = ?", p2, session["user_id"])
        p3 = request.form.get("pic3")
        if (p3):
            db.execute("UPDATE users SET p3 = ? WHERE id = ?", p3, session["user_id"])
        p4 = request.form.get("pic4")
        if (p4):
            db.execute("UPDATE users SET p4 = ? WHERE id = ?", p4, session["user_id"])
        p5 = request.form.get("pic5")
        if (p5):
            db.execute("UPDATE users SET p5 = ? WHERE id = ?", p5, session["user_id"])
        p6 = request.form.get("pic6")
        if (p6):
            db.execute("UPDATE users SET p6 = ? WHERE id = ?", p6, session["user_id"])

        #grab info from HTML profile qs
    #Gender
        gender = request.form.get("gender")
        if (gender):
            db.execute("UPDATE users SET gender = ? WHERE id = ?", gender, session["user_id"])

    #Gender Coliving Preference
        gender_comfort = request.form.getlist("gender_comfort")
        gender_pref = ""
        for i in range(len(gender_comfort)):
            gender_pref = gender_pref + gender_comfort[i]
        if (gender_comfort):
            db.execute("UPDATE users SET gender_comfort = ? WHERE id = ?", gender_pref, session["user_id"])

    #Pets
        pets_test = request.form.getlist("pets_test")
        pet_pref = ""
        for i in range(len(pets_test)):
            pet_pref = (pet_pref + pets_test[i])
            #print(pet_pref)
        if (pets_test):
            db.execute("UPDATE users SET pets_test = ? WHERE id = ?", pet_pref, session["user_id"])

    #Distance
        distance_pref = request.form.get("distance")
        if (distance_pref):
            db.execute("UPDATE users SET distance_pref = ? WHERE id = ?", distance_pref, session["user_id"])

        #Bio
        bio = request.form.get("bio")
        if (bio):
            db.execute("UPDATE users SET bio = ? WHERE id = ?", bio, session["user_id"])

        return redirect("/profile") 
    else:
        return render_template("profile.html")

#delete PROFILE pictures
@app.route("/x_profile", methods=["Get", "POST", "DELETE"])
@login_required
def x_profile():
    pp = db.execute("SELECT profile_pic_test FROM users WHERE id = ?", session["user_id"])
    pp = pp[0]["profile_pic_test"]
    if request.method == "POST":
        db.execute("UPDATE users SET profile_pic_test = null WHERE id = ?", session["user_id"])
    return redirect("/profile")

@app.route("/x_p2", methods=["Get", "POST", "DELETE"])
@login_required
def x_p2():
    p2 = db.execute("SELECT p2 FROM users WHERE id = ?", session["user_id"])
    p2 = p2[0]["p2"]
    if request.method == "POST":
        db.execute("UPDATE users SET p2 = null WHERE id = ?", session["user_id"])
    return redirect("/profile")

@app.route("/x_p3", methods=["Get", "POST", "DELETE"])
@login_required
def x_p3():
    p3 = db.execute("SELECT p3 FROM users WHERE id = ?", session["user_id"])
    p3 = p3[0]["p3"]
    if request.method == "POST":
        db.execute("UPDATE users SET p3 = null WHERE id = ?", session["user_id"])
    return redirect("/profile")

@app.route("/x_p4", methods=["Get", "POST", "DELETE"])
@login_required
def x_p4():
    p4 = db.execute("SELECT p4 FROM users WHERE id = ?", session["user_id"])
    p4 = p4[0]["p4"]
    if request.method == "POST":
        db.execute("UPDATE users SET p4 = null WHERE id = ?", session["user_id"])
    return redirect("/profile")
    
@app.route("/x_p5", methods=["Get", "POST", "DELETE"])
@login_required
def x_p5():
    p5 = db.execute("SELECT p5 FROM users WHERE id = ?", session["user_id"])
    p5 = p5[0]["p5"]
    if request.method == "POST":
        db.execute("UPDATE users SET p5 = null WHERE id = ?", session["user_id"])
    return redirect("/profile")
    
@app.route("/x_p6", methods=["Get", "POST", "DELETE"])
@login_required
def x_p6():
    p6 = db.execute("SELECT p6 FROM users WHERE id = ?", session["user_id"])
    p6 = p6[0]["p6"]
    if request.method == "POST":
        db.execute("UPDATE users SET p6 = null WHERE id = ?", session["user_id"])
    return redirect("/profile")


#delete pictures
@app.route("/x_h1", methods=["Get", "POST", "DELETE"])
@login_required
def x_h1():
    h1 = db.execute("SELECT h1 FROM users WHERE id = ?", session["user_id"])
    h1 = h1[0]["h1"]
    if request.method == "POST":
        db.execute("UPDATE users SET h1 = null WHERE id = ?", session["user_id"])
    return redirect("/home_test")

@app.route("/x_h2", methods=["Get", "POST", "DELETE"])
@login_required
def x_h2():
    h2 = db.execute("SELECT h2 FROM users WHERE id = ?", session["user_id"])
    h2 = h2[0]["h2"]
    if request.method == "POST":
        db.execute("UPDATE users SET h2 = null WHERE id = ?", session["user_id"])
    return redirect("/home_test")

@app.route("/x_h3", methods=["Get", "POST", "DELETE"])
@login_required
def x_h3():
    h3 = db.execute("SELECT h3 FROM users WHERE id = ?", session["user_id"])
    h3 = h3[0]["h3"]
    if request.method == "POST":
        db.execute("UPDATE users SET h3 = null WHERE id = ?", session["user_id"])
    return redirect("/home_test")

@app.route("/x_h4", methods=["Get", "POST", "DELETE"])
@login_required
def x_h4():
    h4 = db.execute("SELECT h4 FROM users WHERE id = ?", session["user_id"])
    h4 = h4[0]["h4"]
    if request.method == "POST":
        db.execute("UPDATE users SET h4 = null WHERE id = ?", session["user_id"])
    return redirect("/home_test")

@app.route("/x_h5", methods=["Get", "POST", "DELETE"])
@login_required
def x_h5():
    h5 = db.execute("SELECT h5 FROM users WHERE id = ?", session["user_id"])
    h5 = h5[0]["h5"]
    if request.method == "POST":
        db.execute("UPDATE users SET h5 = null WHERE id = ?", session["user_id"])
    return redirect("/home_test")

@app.route("/x_h6", methods=["Get", "POST", "DELETE"])
@login_required
def x_h6():
    h6 = db.execute("SELECT h6 FROM users WHERE id = ?", session["user_id"])
    h6 = h6[0]["h6"]
    if request.method == "POST":
        db.execute("UPDATE users SET h6 = null WHERE id = ?", session["user_id"])
    return redirect("/home_test")


@app.route("/message", methods=["GET", "POST"])
@login_required
def message():
    likes_you = []
    matches = []
    you_like = db.execute("SELECT DISTINCT other_username FROM likes WHERE user_id == ? AND like == 'yes'", session["user_id"])
    like_you = db.execute("SELECT DISTINCT username FROM likes WHERE other_user_id == ? AND like == 'yes'", session["user_id"])
    for i in like_you:
        likes_you.append(i['username'])
    for i in range(len(you_like)):
        if you_like[i]['other_username'] in likes_you:
            matches.append(you_like[i]['other_username'])
    matches_len = len(matches)

    #grab data of matched users (this can be used to find profile pics)
    match_list = []
    for i in matches:
        data = db.execute("SELECT * FROM users WHERE username == ?", i)
        match_list.append(data)

    #send messages to HMTL. Send user_id for jinja to know where to put which message.
    messages = db.execute("SELECT * from MESSAGES WHERE user_id = ? OR other_user_id = ? ORDER BY timestamp ASC", session["user_id"], session["user_id"])
    messages_len = len(messages)
    current_user_id = session["user_id"]

    #Variables for updating SQL
    user = db.execute('SELECT * FROM users WHERE id = ?', session["user_id"])
    current_username = user[0]['username']
    other_username = matches[0]
    other_user_id = db.execute('SELECT id FROM users WHERE username = ?', other_username)
    other_user_id = other_user_id[0]['id']

    print("\n\nyou_like: ", you_like, "\nlike_you: ", like_you, "\nlikes_you: ", likes_you, "\n\n")
    print("\n\nmatches: ", matches, "\nmatch_len: ", matches_len, "\nmatch_list: ", match_list, "\n\nmessages:", messages, "\n\n")
    
    #your pp
    pp = db.execute("SELECT profile_pic_test FROM users WHERE id = ?", session["user_id"])
    pp = pp[0]["profile_pic_test"]
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username[0]["username"]




    if request.method == "GET":
        return render_template("messages.html", username=username, pp=pp, messages=messages, messages_len=messages_len, matches=matches, current_user_id=current_user_id, matches_len=matches_len, match_list=match_list)

    elif request.method == "POST":
        print("\n\ncurrent_username: ", current_username, "\nother_username: ", other_username, "\other_user_id: ", other_user_id, "\n\n")
        new_message = request.form.get("new_message")
        db.execute("INSERT INTO messages (user_id, username, other_username, other_user_id, message) VALUES (?, ?, ?, ?, ?)", session["user_id"], current_username, other_username, other_user_id, new_message)
        messages = db.execute("SELECT * from MESSAGES WHERE user_id = ? OR other_user_id = ? ORDER BY timestamp ASC", session["user_id"], session["user_id"])
        messages_len = len(messages)
        return render_template("messages.html", username=username, pp=pp, messages=messages, messages_json=json.dumps(messages), messages_len=messages_len, matches=matches, current_user_id=current_user_id, matches_len=matches_len, match_list=match_list)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("You didn't choose a username", 403)

        # ensure password is at least 8 characters long
        #elif len(request.form.get("password")) < 8:
            #return apology("Password must be at least 8 characters")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # ensure confirm password was submitted AND is equal to password
        elif not request.form.get("confirmation") or request.form.get("confirmation") != request.form.get("password"):
            return apology("Passwords do not match", 403)

        # ensure username is not already taken
        elif db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username")):
            return apology("Username already taken")

        # generate a hash using the password
        pw = request.form.get("password")
        hash = generate_password_hash(pw)

        # Store all of the data in SQL databases - users and stocks
        username = request.form.get("username")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        newid = (db.execute("SELECT id FROM users WHERE username = %s", username))

        # return to homepage
        return redirect("/")

        #If register is reached via GET
    else:
        return render_template("register.html")


@app.route("/home_test", methods=["GET", "POST"])
@login_required
def home_test():
    pp = db.execute("SELECT profile_pic_test FROM users WHERE id = ?", session["user_id"])
    pp = pp[0]["profile_pic_test"]
    h1 = db.execute("SELECT h1 FROM users WHERE id = ?", session["user_id"])
    h2 = db.execute("SELECT h2 FROM users WHERE id = ?", session["user_id"])
    h3 = db.execute("SELECT h3 FROM users WHERE id = ?", session["user_id"])
    h4 = db.execute("SELECT h4 FROM users WHERE id = ?", session["user_id"])
    h5 = db.execute("SELECT h5 FROM users WHERE id = ?", session["user_id"])
    h6 = db.execute("SELECT h6 FROM users WHERE id = ?", session["user_id"])
    h1 = h1[0]["h1"]
    h2 = h2[0]["h2"]
    h3 = h3[0]["h3"]
    h4 = h4[0]["h4"]
    h5 = h5[0]["h5"]
    h6 = h6[0]["h6"]
    house_description = db.execute("SELECT house_description FROM users WHERE id = ?", session["user_id"])
    home = [h1, h2, h3, h4, h5, h6]
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username[0]["username"]

    if request.method == "GET":

        print("\n1: ", h1, "\n2: ", h2, "\n3: ", h3, "\n4: ", h4, "\n5: ", h5, "\n6: ", h6, "\n")
        print(pp)
        print("")
        
        return render_template("home_test.html", house_description=house_description, pp=pp, home=home, username=username, h1=h1, h2=h2, h3=h3, h4=h4, h5=h5, h6=h6)
    else:
        #grab uploaded pics from HTML
        h1 = request.form.get("h1")
        if (h1):
            db.execute("UPDATE users SET h1 = ? WHERE id = ?", h1, session["user_id"])
        h2 = request.form.get("h2")
        if (h2):
            db.execute("UPDATE users SET h2 = ? WHERE id = ?", h2, session["user_id"])
        h3 = request.form.get("h3")
        if (h3):
            db.execute("UPDATE users SET h3 = ? WHERE id = ?", h3, session["user_id"])
        h4 = request.form.get("h4")
        if (h4):
            db.execute("UPDATE users SET h4 = ? WHERE id = ?", h4, session["user_id"])
        h5 = request.form.get("h5")
        if (h5):
            db.execute("UPDATE users SET h5 = ? WHERE id = ?", h5, session["user_id"])
        h6 = request.form.get("h6")
        if (h6):
            db.execute("UPDATE users SET h6 = ? WHERE id = ?", h6, session["user_id"])
        house_description = request.form.get("house_description")
        if (house_description):
            db.execute("UPDATE users SET house_description = ? WHERE id = ?", house_description, session["user_id"])
        return redirect("/home_test")


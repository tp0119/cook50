import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cookbook.db")

@app.route("/")
@login_required
def index():
    """Show cookbook"""

    # get all of user's recipes from databse
    rows = db.execute("SELECT * FROM recipes WHERE user_id = :user_id", user_id=session["user_id"])
    length = len(rows)
    # rows is list of dictionaries

    # send index.html the list of dictionaries (rows)
    return render_template("index.html", length=length, rows=rows)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add new recipe to cookbook"""

    if request.method == "GET":
        return render_template("add.html")
    else:
        name = request.form.get("name")
        rating = request.form.get("rating")
        difficulty = request.form.get("difficulty")
        mealtype = request.form.get("type")
        preptime = request.form.get("preptime")
        lastmade = request.form.get("lastmade")
        url = request.form.get("url")

        # check if all ingredient fields are entered, otherwise store "No ingredients listed" in i1
        main_ing1 = request.form.get("i1")
        main_ing2 = request.form.get("i2")
        main_ing3 = request.form.get("i3")
        main_ing4 = request.form.get("i4")
        main_ing5 = request.form.get("i5")
        if not main_ing1 and not main_ing2 and not main_ing3 and not main_ing4 and not main_ing5:
            i1 = "No ingredients listed"
            i2 = main_ing2
            i3 = main_ing3
            i4 = main_ing4
            i5 = main_ing5
        else:
            i1 = main_ing1
            i2 = main_ing2
            i3 = main_ing3
            i4 = main_ing4
            i5 = main_ing5

        # render apology if no name entered
        if not name:
            return apology("Missing name")

        # insert new recipe into database
        db.execute("INSERT INTO recipes (user_id, name, rating, difficulty, mealtype, preptime, lastmade, url, i1, i2, i3, i4, i5) VALUES (:user_id, :name, :rating, :difficulty, :mealtype, :preptime, :lastmade, :url, :i1, :i2, :i3, :i4, :i5)", user_id=session["user_id"], name=name, rating=rating, difficulty=difficulty, mealtype=mealtype, preptime=preptime, lastmade=lastmade, url=url, i1=i1, i2=i2, i3=i3, i4=i4, i5=i5)

    return redirect("/")


@app.route("/timer", methods=["GET", "POST"])
@login_required
def timer():
    """Display a timer given hours and minutes"""

    if request.method == "GET":
        return render_template("timer.html")
    else:
        hours = request.form.get("hours")
        minutes = request.form.get("minutes")

    return render_template("timerdisplay.html", hours=hours, minutes=minutes)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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


@app.route("/shoppinglist", methods=["GET", "POST"])
@login_required
def shoppinglist():
    """Display, add, & delete items on shopping list"""

    if request.method == "GET":
        # get user's items from shoppinglist table in database
        rows = db.execute("SELECT * FROM shoppinglist WHERE user_id = :user_id", user_id=session["user_id"])
        length = len(rows)
        return render_template("shoppinglist.html", rows=rows, length=length)
    else:
        item = request.form.get("item")
        q = request.form.get("quantity")

        # if no quantity is entered by user, set default quantity to 1
        if not q:
            quantity = 1
        else:
            quantity = int(q)

        # render apology if user clicks "Add" w/out entering an item name
        if not item:
            return apology("Missing Item")

        # if item is already on your list, update quantity, otherwise add the item to the list
        repeat = db.execute("SELECT * FROM shoppinglist WHERE user_id = :user_id AND item = :item", user_id=session["user_id"], item=item)
        if len(repeat) > 0:
            old_quantity = int(repeat[0]["quantity"])
            new_quantity = quantity + old_quantity
            db.execute("UPDATE shoppinglist SET quantity = :new_quantity WHERE user_id = :user_id AND item = :item", new_quantity=new_quantity, user_id=session["user_id"], item=item)
        else:
            db.execute("INSERT INTO shoppinglist (user_id, item, quantity) VALUES (:user_id, :item, :quantity)", user_id=session["user_id"], item=item, quantity=quantity)

        rows = db.execute("SELECT * FROM shoppinglist WHERE user_id = :user_id", user_id=session["user_id"])
        length = len(rows)

    return render_template("shoppinglist.html", rows=rows, length=length)

@app.route("/remove", methods=["POST"])
@login_required
def remove():
    """Remove items from shopping list"""

    item_id = request.form.get("item_id")
    db.execute("DELETE FROM shoppinglist WHERE user_id = :user_id AND id = :item_id", user_id=session["user_id"], item_id=item_id)

    return redirect("/shoppinglist")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")

        # render apology if username is blank
        if not username:
            return apology("You must provide a username")

        # render apology if username is taken
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) > 0:
            return apology("This username is already taken")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # render apology if password is blank
        if not password:
            return apology("Missing Password")

        # render apology if password and confirmation do not match
        if password != confirmation:
            return apology("Passwords don't match")

        # hash password if user enters all fields correctly
        pwhash = generate_password_hash(password);
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :pwhash)", username=username, pwhash=pwhash)

        return redirect("/")


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    """Delete items from meal planner"""

    item_id = request.form.get("item_id")
    db.execute("DELETE FROM planner WHERE user_id = :user_id AND id = :item_id", user_id=session["user_id"], item_id=item_id)

    return redirect("/planner")


@app.route("/delete2", methods=["POST"])
@login_required
def delete2():
    """Delete recipes from cookbook"""

    recipe_id = request.form.get("recipe_id")
    db.execute("DELETE FROM recipes WHERE user_id = :user_id AND id = :recipe_id", user_id=session["user_id"], recipe_id=recipe_id)

    return redirect("/")

@app.route("/search", methods=["POST"])
@login_required
def search():
    """Search for a recipe by name"""

    recipe_name = request.form.get("recipe_name")
    rows = db.execute("SELECT * FROM recipes WHERE user_id = :user_id AND name = :recipe_name", user_id=session["user_id"], recipe_name=recipe_name)
    length = len(rows)

    return render_template("searchresults.html", rows=rows, length=length)

@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    """Plan which recipes to prepare in the coming week"""

    recipes = db.execute("SELECT * FROM recipes WHERE user_id = :user_id", user_id=session["user_id"])
    length = len(recipes)

    if request.method == "GET":
        # get lists of recipes corresponding to each day of the week from the planner table in database

        # Sunday
        sun = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="sun")
        sun_length = len(sun)
        # Monday
        mon = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="mon")
        mon_length = len(mon)
        # Tuesday
        tue = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="tue")
        tue_length = len(tue)
        # Wednesday
        wed = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="wed")
        wed_length = len(wed)
        # Thursday
        thu = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="thu")
        thu_length = len(thu)
        # Friday
        fri = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="fri")
        fri_length = len(fri)
        # Saturday
        sat = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="sat")
        sat_length = len(sat)

        return render_template("planner.html", sun=sun, sun_length=sun_length, mon=mon, mon_length=mon_length, tue=tue, tue_length=tue_length, wed=wed, wed_length=wed_length, thu=thu, thu_length=thu_length, fri=fri, fri_length=fri_length, sat=sat, sat_length=sat_length, recipes=recipes, length=length)
    else:
        day = request.form.get("day")
        mealtype = request.form.get("type")
        name = request.form.get("recipe")

        # insert the chosen recipe, day of the week, and meal type into the planner table in the database
        db.execute("INSERT INTO planner (user_id, day, mealtype, name) VALUES (:user_id, :day, :mealtype, :name)", user_id=session["user_id"], day=day, mealtype=mealtype, name=name)

        # get lists of recipes corresponding to each day of the week from the planner table in database

        # Sunday
        sun = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="sun")
        sun_length = len(sun)
        # Monday
        mon = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="mon")
        mon_length = len(mon)
        # Tuesday
        tue = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="tue")
        tue_length = len(tue)
        # Wednesday
        wed = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="wed")
        wed_length = len(wed)
        # Thursday
        thu = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="thu")
        thu_length = len(thu)
        # Friday
        fri = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="fri")
        fri_length = len(fri)
        # Saturday
        sat = db.execute("SELECT * FROM planner WHERE user_id = :user_id AND day = :day", user_id=session["user_id"], day="sat")
        sat_length = len(sat)

        return render_template("planner.html", sun=sun, sun_length=sun_length, mon=mon, mon_length=mon_length, tue=tue, tue_length=tue_length, wed=wed, wed_length=wed_length, thu=thu, thu_length=thu_length, fri=fri, fri_length=fri_length, sat=sat, sat_length=sat_length, recipes=recipes, length=length)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

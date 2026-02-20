from cs50 import SQL
from flask import Flask, render_template, redirect, request, session, jsonify
from flask_session import Session
from helpers import error, login_required, check_fivlet, fivlet_dictionary
import random

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# To access the database file
db = SQL("sqlite:///fivlet.db")

# Creating a list of five-letter words
with open("en", "r") as file:
    
    # Selecting all the words from the dictionary
    words = file.read().splitlines()

    # Selecting only the five letter words
    valid_words = [word.upper() for word in words if len(word) == 5]

# Accessing the five-letter word dictionary (from helpers) that has COMMON five-letter words for fivlet
fivlet_words = fivlet_dictionary()


# Defining number of chances and Player ranks
attempts = 5
tags = ["Novice", "Trainee", "Practitioner", "Competent", "Skilled", "Advanced", "Expert", "Specialist", "Master", "Grandmaster"]

# Main page of the game
@app.route("/")
@login_required
def index():
    """The Main Page of the Game"""

    # Pick a random word for each game
    fivlet = random.choice(fivlet_words)

    # Forgetting the previos word
    if "fivlet" in session:
        session.pop("fivlet", None)
    
    # Store the new word in the current session
    session["fivlet"] = fivlet
    
    # Selecting the username from the database of the current user
    username_dict = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username_dict[0]["username"]
    return render_template("index.html", username=username, rows=attempts)

# Validation
@app.route("/validation", methods=["POST"])
@login_required
def validation():
    """Validating User's Guess"""

    # Getting the user's typed word and current attempt number(row) from JavaScript (POST)
    data = request.get_json()
    guess = data.get("word")
    row = data.get("row")

    # Check whether the user's typed word exists or not
    guessed_word = True
    if guess not in valid_words:
        guessed_word = False
        return jsonify(guessed_word)

    # Getting the fivlet word
    fivlet = session["fivlet"]
    
    # Function will return a dictionary after the validation of the user's word
    result = check_fivlet(fivlet, guess)

    # If this is the last attempt of the user and their guess is still wrong
    if row == attempts - 1 and result["type"] != "win":
        result["type"] = "lost"
        result["word"] = fivlet
    
    if result["type"] != "try_again":
        db.execute("INSERT INTO performance (user_id, attempts, status) VALUES (?, ?, ?)", session["user_id"], row + 1, result["type"])
    
    return jsonify(result)


# Revealing the word if the user gives up
@app.route("/reveal", methods=["POST"])
@login_required
def reveal():
    """Revealing the actual Fivlet word"""

    # Selecting the number of attempts made by the user before giving up
    data = request.get_json()
    chances = data.get("row")

    # Updating the user's performance in the database
    db.execute("INSERT INTO performance (user_id, attempts, status) VALUES (?, ?, ?)", session["user_id"], chances, "give_up")

    # Inserting the Fivlet word into dictionary
    result = {"word": session["fivlet"]}

    return jsonify(result)


# Showing the user the status of their performance
@app.route("/status")
@login_required
def status():
    """To Show the alltime performance"""
    
    # Selecting the all time performance of the current user
    player_stat = db.execute("SELECT * FROM performance WHERE user_id = ?", session["user_id"])

    # Creating a dictionary to store the percentage of winning and losing and giving up
    overall = {}

    # Selecting total number of games played by the current user
    games_played_dict = db.execute("SELECT COUNT(*) as games FROM performance WHERE user_id = ?", session["user_id"])
    games_played = games_played_dict[0]["games"]
    # Selecting total number of correct guesses
    games_won_dict = db.execute("SELECT COUNT(*) as won FROM performance WHERE user_id = ? AND status = ?", session["user_id"], "win")
    games_won = games_won_dict[0]["won"]
    # Selecting total number of wrong guesses
    games_lost_dict = db.execute("SELECT COUNT(*) as lost FROM performance WHERE user_id = ? AND status = ?", session["user_id"], "lost")
    games_lost = games_lost_dict[0]["lost"]
    # Selecting total number of giving ups
    games_give_up_dict = db.execute("SELECT COUNT(*) as give_up FROM performance WHERE user_id = ? AND status = ?", session["user_id"], "give_up")
    games_give_up = games_give_up_dict[0]["give_up"]

    # Updating the overall performance dictionary with necessary details
    overall["total"] = games_played
    overall["won"] = games_won
    overall["lost"] = games_lost
    
    # if the player has not played any games
    if games_played == 0:
        overall["win_percent"] = 0
        overall["loss_percent"] = 0
        overall["giveup_percent"] = 0
    else:    
        overall["win_percent"] = (games_won * 100) / games_played
        overall["loss_percent"] = (games_lost * 100) / games_played
        overall["giveup_percent"] = (games_give_up * 100) / games_played

    tag_value = min(int(overall["win_percent"] // 10), 9)

    overall["tag"] = tags[tag_value]

    return render_template("status.html", performances=player_stat, overall=overall)

    
    


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Registering a New User"""
    
    if request.method == "POST":
        # Getting the username
        username = request.form.get("username")
        # If the user provides nothing
        if not username:
            return error("Username is Blank", 400)
        
        # Checking if the username already exists in the database
        exist = db.execute("SELECT id FROM users WHERE username = ?", username)
        if exist:
            return error("Username already exists! Try a different one", 400)
        
        # Registering the user in the database
        db.execute("INSERT INTO users (username) VALUES (?)", username)

        # Directly logging in the user
        id_dict = db.execute("SELECT id FROM users WHERE username = ?", username)
        session["user_id"] = id_dict[0]["id"]
        return redirect("/")
    else:
        return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log the User in"""
    
    # Forget any user id
    session.clear()
    
    if request.method == "POST":
        # Getting the input from the login username field
        username = request.form.get("username")
        # If the user does not provide any inputs
        if not username:
            return error("Username is Blank", 400)
        
        # Checking database if the username exists
        user_dict = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user_dict) != 1:
            return error("Username does not exist", 400)
        
        # Remembering the user using session
        session["user_id"] = user_dict[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")
    
# Logout
@app.route("/logout")
def logout():
    """Log the User out"""

    # Clearing existing session
    session.clear()

    return redirect("/login")


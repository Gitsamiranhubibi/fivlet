from flask import render_template, redirect, session
from functools import wraps


# Showing error message if the user fails to provide valid info
def error(message, code=400):
    """Render message as an error to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("error.html", top=code, bottom=escape(message)), code


# A function that will make sure that the user is logged in before going to the URLs of
# main game or status
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Function that checks whether the user's typed word and the original fivlet word matches or not
def check_fivlet(fivlet, guess):

    letters = set(list(fivlet))

    appear = {}
    for letter in letters:
        count = 0
        for i in range(5):
            if letter == fivlet[i]:
                count += 1

        appear[letter] = count
            

    colors = []
    for i in range(5):
        if fivlet[i] == guess[i]:
            colors.append("green")
            appear[fivlet[i]] -= 1
        else:
            colors.append("?")

    for i in range(len(colors)):
        if colors[i] == "?":
            if guess[i] in letters and appear[guess[i]] > 0:
                colors[i] = "yellow"
                appear[guess[i]] -= 1
            else:
                colors[i] = "grey"


    result = {}

    if fivlet == guess:
        result["colors"] = ["green", "green", "green", "green", "green"]
        result["type"] = "win"
    else:
        result["colors"] = colors
        result["type"] = "try_again"
    
    return result


# A FUNCTION that will return a dictionary of five letter words
def fivlet_dictionary():

    # Creating a dictionary with five letter words
    dictionary = [
        "apple", "grape", "plane", "chair", "table", "graph", "brand", "glass", "craft", "watch", "shelf",
        "spoon", "brush", "tiger", "flame", "storm", "floor", "paint", "curve", "slice", "price", "flour",
        "heavy", "heart", "ready", "trace", "bring", "crash", "faint", "eager", "delay", "inner", "clash",
        "power", "lower", "start", "twins", "fried", "outer", "shady", "sunny", "rainy", "alley", "funny",
        "grade", "brave", "great", "scold", "borne", "boast", "bride", "cider", "dozen", "eagle", "tribe",
        "bread", "plant", "grass", "cloud", "water", "ferry", "grove", "ivory", "canoe", "purge", "flirt",
        "stone", "river", "night", "light", "dance", "metal", "mimic", "niece", "ounce", "prune", "crown",
        "smile", "happy", "angry", "sweet", "horse", "quilt", "rider", "thorn", "stare", "scone", "glare",
        "peace", "fight", "zebra", "mango", "lemon", "unify", "vapor", "whisk", "yodel", "mason", "elder",
        "berry", "crisp", "track", "train", "earth", "flora", "comic", "polar", "karma", "forge", "cedar",
        "ocean", "dream", "magic", "quiet", "quite", "curry", "badge", "intel", "fable", "bacon", "mulch",
        "noisy", "music", "sugar", "honey", "ghost", "amber", "feast", "chute", "clasp", "deity", "clone",
        "angel", "fairy", "ghost", "tears", "arrow", "bevel", "blown", "jumpy", "kneel", "fauna", "basil",
        "bloom", "clown", "blaze", "brick", "clock", "admit", "flick", "ebony", "coral", "aspen", "grant",
        "draft", "dress", "frost", "glove", "hatch", "charm", "harem", "abode", "habit", "acute", "aisle",
        "jelly", "knife", "layer", "ledge", "globe", "caper", "gorge", "balmy", "claim", "elbow", "frown",
        "quirk", "mirth", "dwell", "visit", "swell", "vivid", "straw", "prism", "flock", "spice", "crane",
        "gleam", "raven", "oxide", "sworn", "sting", "piano", "lunar", "noble", "novel", "super", "space",
        "march", "cabin", "pouch", "trail", "fiber", "spine", "whale", "zonal", "cubik", "trunk", "stink",
        "vowel", "scarf", "arena", "plush", "tempo", "wheat", "scent", "motel", "nurse", "elude", "harsh",
    ]

    dictionary = [word.upper() for word in dictionary]

    return dictionary


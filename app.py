import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)

# Home Page
@app.route("/")
@app.route('/home_page')
def home_page():
    """
    index page to be displayed.
    """
    return render_template("index.html")



# All recipes
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


# Individual recipe 
@app.route("/recipe/<recipe_id>")
def recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe.html", recipe=recipe)



# Search Bar 
@app.route("/search", methods=["GET", "POST"])
def search():
    search_recipe = request.form.get("search_recipe")
    recipes = mongo.db.recipes.find({"$text": {"$search": search_recipe}})
    return render_template("recipes.html", recipes=recipes)

"""
# Filter
@app.route("/filter", methods=["GET", "POST"])
def filter():
    # find category names from mongodb
    categories = mongo.db.categories.find().sort("category_name", 1)
    # Select by category name 
    category_name_search = request.form.get("category_name_search")
    recipes = mongo.db.recipes.find({
        "$text": {"$search": '"'+category_name_search+'"'}}).sort("recipe_name", 1)
    
    # Search results found
    return render_template("recipes.html", recipe_name=recipe_name,
    category_name=category_name)
"""

# Registration 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method  == "POST":
        # verify if the username already exists in datebase
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # flash message to show user already exists
        if existing_user:
            flash("Username already exists")
            # redirect user back to register form
            return redirect(url_for("register"))
            
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "profile_image": request.form.get("profile_image"),
            "about": request.form.get("about")
        }
        mongo.db.users.insert_one(register)

        # new user into session using session cookie
        session["users"] = request.form.get("username").lower()
        # flash message confiriming registration successful
        flash("Registration Successful")
    return render_template("register.html")


    # User Log In
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
         # verify if the username already exists in datebase
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Hashed password matches user password input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    # Session variable with User cookie
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}!".format(request.form.get("username")))
            else:
                # Password does not match
                flash("Incorrect Username or Password")
                return redirect(url_for("login"))
        else:
            # Username does not match
            flash("Incorrect Username or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
        # change to False for submission
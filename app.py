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


# all recipes
@app.route("/get_recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


# individual recipe
@app.route("/recipe/<recipe_id>")
def recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe.html", recipe=recipe)


# search bar 
@app.route("/search", methods=["GET", "POST"])
def search():
    search_recipe = request.form.get("search_recipe")
    recipes = mongo.db.recipes.find({"$text": {"$search": search_recipe}})
    return render_template("recipes.html", recipes=recipes)


# registration 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST": 
        # Verify if the username already exists in datebase
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # flash message to show user already exists
        if existing_user:
            flash("Username already exists")
            # redirect user back to register form
            return redirect(url_for("register"))      
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(
                request.form.get("password")),
            "profile_image": request.form.get("profile_image"),
            "about": request.form.get("about")
        }         
        mongo.db.users.insert_one(register)

        # new user into session using session cookie
        session["users"] = request.form.get("username").lower()
        # flash message confiriming registration successful
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["users"]))    
    return render_template("register.html")


# user Log In
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # verify if the username already exists in datebase
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # hashed password matches user password input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}!".format(
                            request.form.get("username")))
                    return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # Password does not match
                flash("Incorrect Username or Password")
                return redirect(url_for("login"))
        else:
            # Username does not match
            flash("Incorrect Username or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Profile
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Get the sessions user's username from database
    user = mongo.db.users.find_one({"username": username.lower()})
    recipes = list(mongo.db.recipes.find({"created_by": username.lower()}))

    if "user" in session:
        return render_template("profile.html", user=user, recipes=recipes)

    return redirect(url_for("login"))


# Edit Profile
@app.route("/edit_profile/<username>", methods=["GET", "POST"])
def edit_profile(username):
    user = mongo.db.users.find_one({"username": username.lower()})
    if request.method == "POST":
        # key value pairs
        edit = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(
                request.form.get("password")),
            "profile_image": request.form.get("profile_image"),
            "about": request.form.get("about")
        }
        mongo.db.users.update({"username": username.lower()}, edit)
        flash("Profile Successfully Updated")   

    if "user" in session:
            return render_template("edit_profile.html", user=user)

    return redirect(url_for("login"))


# Delete Profile
@app.route("/delete_profile/<username>")
def delete_profile(username):
    mongo.db.users.remove({"username": username.lower()})
    flash("Profile Successfully Deleted")
    # remove the username from the session 
    session.pop("user")

    return redirect(url_for("register"))


# Log out
@app.route("/logout")
def logout():
    # remove the user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# View all users on db
@app.route("/all_users")
def all_users():
    users = list(mongo.db.users.find())

    if "user" in session:
        return render_template("all_users.html", users=users)

    return redirect(url_for("login"))


# Recipe CRUD Funtionality
# Add/Create a new recipe
@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        # key value pairs
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_image": request.form.get("recipe_image"),
            "recipe_description": request.form.get("recipe_description"),
            "ingredients_list": request.form.get("ingredients_list"),
            "method_step1": request.form.get("method_step1"),
            "method_step2": request.form.get("method_step2"),
            "category_name": request.form.get("category_name"),
            "preparation_time": request.form.get("preparation_time"),
            "difficulty": request.form.get("difficulty"),
            "created_by": session["user"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for('add_recipe'))

    # Get data from categories collection in database
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


# Update Recipe 
@app.route("/update_recipe/<recipe_id>", methods=["GET", "POST"])
def update_recipe(recipe_id):
    if request.method == "POST":
        # key value pairs
        submit = {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_image": request.form.get("recipe_image"),
            "recipe_description": request.form.get("recipe_description"),
            "ingredients_list": request.form.get("ingredients_list"),
            "method_step1": request.form.get("method_step1"),
            "method_step2": request.form.get("method_step2"),
            "category_name": request.form.get("category_name"),
            "preparation_time": request.form.get("preparation_time"),
            "difficulty": request.form.get("difficulty"),
            "created_by": session["user"]
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe Successfully Updated")      

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "update_recipe.html", recipe=recipe, categories=categories)


# Delete Recipe
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("get_recipes"))

"""
Categories CRUD Functionality
"""   


# Categories
@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


# Add Category
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
         "category_name": request.form.get("category_name")   
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Successfully Added")
        return redirect(url_for('get_categories'))

    return render_template("add_category.html")


# Edit Category
@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
         "category_name": request.form.get("category_name")   
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for('get_categories'))
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


# Delete Category
@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False) 
# change to False for submission
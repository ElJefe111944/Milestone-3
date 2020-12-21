import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
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



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
        # change to False for submission
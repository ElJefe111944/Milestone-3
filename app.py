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

# Home
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
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)



@app.route("/search", methods=["GET", "POST"])
def search():
    search_recipe = request.form.get("search_recipe")
    recipes = mongo.db.recipes.find({"$text": {"$search": search_recipe}})
    return render_template("recipes.html", recipes=recipes)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
        # change to False for submission
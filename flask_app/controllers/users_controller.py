from flask import render_template, request, redirect, session
from flask_app import app
from flask_app.models.user_model import User
from flask_app.models.recipe_model import Recipe


# Login and registration form routes
@app.route("/", methods=["GET"])
@app.route("/login", methods=["GET"])
@app.route("/register", methods=["GET"])
def display_login_and_registration():
    return render_template("login_registration.html")


# Register new user route - POST
@app.route("/users/new", methods=["POST"])
def register_user():
    if not User.validate_registration(request.form):
        return redirect("/")

    session["user_id"] = User.create_one(
        {**request.form, "password": User.encrypt_string(request.form["password"])}
    )

    return redirect("/home")


# Login route - POST
@app.route("/users/login", methods=["POST"])
def login():
    email = request.form["login_email"]
    if not User.validate_login_email(email):
        return redirect("/")

    user = User.get_one_by_email({"email": email})

    if not User.validate_password(user.password, request.form["login_password"]):
        return redirect("/")

    session["user_id"] = user.id

    return redirect("/home")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")


# Display homepage route
@app.route("/home", methods=["GET"])
def display_homepage():
    if not "user_id" in session:
        return redirect("/")

    current_user = User.get_one_with_favorites({"id": session["user_id"]})

    list_of_favorites = current_user.list_of_favorites

    for favorite in list_of_favorites:
        print(f"original favorites: {favorite.name}")

    list_of_recipes = Recipe.get_all()

    for recipe in list_of_recipes:
        print(f"original recipes: {recipe.name}")

    for favorite in list_of_favorites:
        for recipe in list_of_recipes:
            if recipe.name == favorite.name:
                list_of_recipes.remove(recipe)

    for recipe in list_of_recipes:
        print(f"updated recipes: {recipe.name}")

    return render_template(
        "recipes_home.html",
        current_user=current_user,
        list_of_recipes=list_of_recipes,
    )


@app.route("/users/<int:recipe_id>/favorites/add", methods=["POST"])
def add_to_favorites(recipe_id):
    User.add_recipe_to_favorites(
        {"user_id": session["user_id"], "recipe_id": recipe_id}
    )

    return redirect("/home")


@app.route("/users/<int:recipe_id>/favorites/remove", methods=["POST"])
def remove_from_favorites(recipe_id):
    User.delete_one_from_favorites(
        {"user_id": session["user_id"], "recipe_id": recipe_id}
    )

    return redirect("/home")

from flask import render_template, request, redirect, session
from flask_app import app
from flask_app.models.recipe_model import Recipe
from flask_app.controllers import users_controller


@app.route("/recipes/new/form", methods=["GET"])
def display_new_recipe_form():
    if not "user_id" in session:
        return redirect("/")

    return render_template("new_recipe_form.html")


@app.route("/recipes/add/new", methods=["POST"])
def add_new_recipe():
    if not "user_id" in session:
        return redirect("/")

    if not Recipe.validate_recipe(request.form):
        return redirect("/recipes/new/form")

    current_user = users_controller.User.get_one({"id": session["user_id"]})

    new_recipe_id = Recipe.create_one({**request.form, "user_id": session["user_id"]})
    print(f"new recipe id: {new_recipe_id}")

    if request.form["add_favorite"] == "Yes":
        current_user.add_recipe_to_favorites(
            {"user_id": current_user.id, "recipe_id": new_recipe_id}
        )

    return redirect("/home")


@app.route("/recipes/<int:id>/delete", methods=["POST"])
def delete_recipe(id):
    if not "user_id" in session:
        return redirect("/")

    Recipe.delete_one({"id": id})

    return redirect("/home")

from flask import render_template, request, redirect, session
from flask_app import app
from flask_app.models.recipe_model import Recipe
from flask_app.controllers import users_controller
from flask_app.models import user_model


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

    new_recipe_id = Recipe.create_one({**request.form, "user_id": session["user_id"]})

    if request.form["add_favorite"] == "Yes":
        user_model.User.add_recipe_to_favorites(
            {"user_id": session["user_id"], "recipe_id": new_recipe_id}
        )

    return redirect("/home")


@app.route("/recipes/<int:id>/delete", methods=["POST"])
def delete_recipe(id):
    if not "user_id" in session:
        return redirect("/")

    Recipe.delete_one({"id": id})

    return redirect("/home")


@app.route("/recipes/<int:id>/view", methods=["GET"])
def display_recipe(id):
    current_user = user_model.User.get_one({"id": session["user_id"]})
    current_recipe = Recipe.get_one_with_favorites({"id": id})

    list_of_favorites = current_recipe.list_of_favorites
    favorites_length = len(list_of_favorites)

    return render_template(
        "display_recipe.html",
        current_user=current_user,
        current_recipe=current_recipe,
        list_of_favorites=list_of_favorites,
        favorites_length=favorites_length,
    )


@app.route("/recipes/<int:id>/edit", methods=["GET"])
def display_edit_recipe_form(id):
    current_recipe = Recipe.get_one({"id": id})
    return render_template("edit_recipe_form.html", current_recipe=current_recipe)


@app.route("/recipes/<int:id>/edit/submit", methods=["POST"])
def update_recipe(id):
    Recipe.update_one({**request.form, "id": id})
    return redirect(f"/recipes/{id}/view")

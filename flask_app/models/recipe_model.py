from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
from flask import flash
from flask_app.models import user_model


class Recipe:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.instructions = data["instructions"]
        self.description = data["description"]
        self.made_on = data["made_on"]
        self.under_30 = data["under_30"]
        self.user_id = data["user_id"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.user = user_model.User.get_one({"id": data["user_id"]})

    @classmethod
    def get_all(cls):
        query = """ 
        SELECT *
        FROM recipes r LEFT JOIN users u
        ON r.user_id = u.id;
        """

        results = connectToMySQL(DATABASE).query_db(query)

        list_of_recipes = []

        for row in results:
            current_recipe = cls(row)
            current_recipe_owner = {
                "id": row["u.id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password": row["password"],
                "created_at": row["u.created_at"],
                "updated_at": row["u.updated_at"],
            }
            current_recipe.user = user_model.User(current_recipe_owner)
            list_of_recipes.append(current_recipe)

        return list_of_recipes

    @classmethod
    def create_one(cls, data):
        query = """ 
        INSERT INTO recipes (name, instructions, description, made_on, under_30, user_id)
        VALUES (%(name)s, %(instructions)s, %(description)s, %(made_on)s, %(under_30)s, %(user_id)s);
        """

        new_recipe_id = connectToMySQL(DATABASE).query_db(query, data)

        return new_recipe_id

    @classmethod
    def delete_one(cls, data):
        query = """ 
        DELETE FROM favorites
        WHERE recipe_id = %(id)s;
        """

        connectToMySQL(DATABASE).query_db(query, data)

        query2 = """ 
        DELETE FROM recipes
        WHERE id = %(id)s;
        """

        connectToMySQL(DATABASE).query_db(query2, data)

    @staticmethod
    def validate_recipe(data):
        is_valid = True
        if len(data["name"]) < 2:
            is_valid = False
            flash(
                "Please provide a valid name for the recipe: at least 2 characters",
                "error_name",
            )
        if len(data["instructions"]) == 0:
            is_valid = False
            flash(
                "Please provide instructions for completing your recipe",
                "error_instructions",
            )
        if len(data["description"]) == 0:
            is_valid = False
            flash(
                "Please provide a description of the recipe",
                "error_description",
            )
        if len(data["made_on"]) == 0:
            is_valid = False
            flash(
                "Please provide the initial date of completion",
                "error_date",
            )
        if not "under_30" in data:
            is_valid = False
            flash(
                "Please confirm the expected time needed to complete this recipe",
                "error_under_30",
            )

        return is_valid

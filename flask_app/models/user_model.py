from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE, EMAIL_REGEX, app
from flask_app.models import recipe_model
from flask import flash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


class User:
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.list_of_recipes = []
        self.list_of_favorites = []

    # Create user
    @classmethod
    def create_one(cls, data):
        query = """ 
        INSERT INTO users (first_name, last_name, email, password)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        """

        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_one(cls, data):
        query = """ 
        SELECT *
        FROM users
        WHERE id = %(id)s;
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        return cls(results[0])

    # Get user with email
    @classmethod
    def get_one_by_email(cls, data):
        query = """ 
        SELECT *
        FROM users
        WHERE email = %(email)s;
        """

        result = connectToMySQL(DATABASE).query_db(query, data)

        if len(result) == 0:
            return None

        print(f"User info: {result[0]}")

        return cls(result[0])

    @classmethod
    def get_one_with_favorites(cls, data):
        query = """ 
        SELECT *
        FROM users u 
        LEFT JOIN favorites f ON f.user_id = u.id
        LEFT JOIN recipes r ON f.recipe_id = r.id
        WHERE u.id = %(id)s;
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        current_user = cls(results[0])

        for row in results:
            if row["r.id"] != None:
                new_favorite = {
                    "id": row["r.id"],
                    "name": row["name"],
                    "instructions": row["instructions"],
                    "description": row["description"],
                    "made_on": row["made_on"],
                    "under_30": row["under_30"],
                    "user_id": row["r.user_id"],
                    "created_at": row["r.created_at"],
                    "updated_at": row["r.updated_at"],
                }
                recipe = recipe_model.Recipe(new_favorite)
                recipe.user = cls.get_one({"id": row["r.user_id"]})
                current_user.list_of_favorites.append(recipe)
        return current_user

    # Add a recipe to the favorites list
    @classmethod
    def add_recipe_to_favorites(cls, data):
        query = """ 
        INSERT INTO favorites (user_id, recipe_id)
        VALUES (%(user_id)s, %(recipe_id)s)
        """

        new_favorite_id = connectToMySQL(DATABASE).query_db(query, data)
        return new_favorite_id

    @classmethod
    def delete_one_from_favorites(cls, data):
        query = """ 
        DELETE FROM favorites f
        WHERE f.user_id = %(user_id)s and f.recipe_id = %(recipe_id)s;
        """

        connectToMySQL(DATABASE).query_db(query, data)

    """ --STATIC METHODS-- """

    # User validation
    @staticmethod
    def validate_registration(data):
        is_valid = True
        if len(data["first_name"]) < 2:
            flash(
                "Please provide a valid name: at least 3 characters", "error_first_name"
            )
            is_valid = False
        if len(data["last_name"]) < 2:
            flash(
                "Please provide a valid name: at least 3 characters", "error_last_name"
            )
            is_valid = False
        if not EMAIL_REGEX.match(data["email"]):
            flash("Please provide a valid email", "error_email")
            is_valid = False
        if len(data["password"]) == 0:
            flash("Please provide a password", "error_password")
            is_valid = False
        if data["confirm_password"] != data["password"]:
            flash("Passwords must match", "error_password")
            is_valid = False
        if User.get_one_by_email(data) != None:
            flash("An account already exists with this email", "error_email")
            is_valid = False
        return is_valid

    # Login email validation
    @staticmethod
    def validate_login_email(email):
        is_valid = True
        if not EMAIL_REGEX.match(email):
            flash("Please provide a valid email address", "error_login_email")
            is_valid = False
        elif User.get_one_by_email({"email": email}) == None:
            flash(
                "No account found. Please check email and try again",
                "error_login_email",
            )
            is_valid = False

        return is_valid

    # Login password validation
    @staticmethod
    def validate_password(hashed_password, unhashed_password):
        is_valid = True
        if len(unhashed_password) == 0:
            flash("Please provide a password", "error_login_password")
            is_valid = False
        if not bcrypt.check_password_hash(hashed_password, unhashed_password):
            flash("Invalid password", "error_login_password")
            is_valid = False

        return is_valid

    # Encrypt password
    @staticmethod
    def encrypt_string(text):
        return bcrypt.generate_password_hash(text)

from flask import render_template, url_for, flash, redirect, request, session
from mycookbook import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from mycookbook.forms import RegisterForm, LoginForm, \
    ChangeUsernameForm, ChangePasswordForm, Add_RecipeForm
import math
import json

# ------------------------------------------------
# HELPER: GET DB CONNECTION
# ------------------------------------------------
def get_conn():
    return db.get_connection()


# ------------------------------------------------
# HOME PAGE
# ------------------------------------------------
@app.route('/')
@app.route('/home')
def home():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM recipes ORDER BY RAND() LIMIT 4")
    featured_recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('home.html', featured_recipes=featured_recipes, title="Home")


# ------------------------------------------------
# ALL RECIPES
# ------------------------------------------------
@app.route('/all_recipes')
def all_recipes():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    limit_per_page = 8
    current_page = int(request.args.get('current_page', 1))

    cursor.execute("SELECT COUNT(*) AS total FROM recipes")
    number_of_all_rec = cursor.fetchone()['total']

    pages = range(1, int(math.ceil(number_of_all_rec / limit_per_page)) + 1)

    cursor.execute("""
        SELECT * FROM recipes ORDER BY id ASC
        LIMIT %s OFFSET %s
    """, (limit_per_page, (current_page - 1) * limit_per_page))
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "all_recipes.html",
        recipes=recipes,
        title="All Recipes",
        current_page=current_page,
        pages=pages,
        number_of_all_rec=number_of_all_rec
    )


# ------------------------------------------------
# SINGLE RECIPE DETAILS
# ------------------------------------------------
@app.route('/recipe_details/<recipe_id>')
def single_recipe_details(recipe_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM recipes WHERE id=%s", (recipe_id,))
    selected_recipe = cursor.fetchone()

    cursor.execute("SELECT username FROM users WHERE id=%s", (selected_recipe['author'],))
    author = cursor.fetchone()['username']

    cursor.close()
    conn.close()

    return render_template("single_recipe_details.html",
                           selected_recipe=selected_recipe,
                           author=author,
                           title='Recipe Details')


# ------------------------------------------------
# MY RECIPES
# ------------------------------------------------
@app.route('/my_recipes/<username>')
def my_recipes(username):
    if 'username' not in session:
        flash('You must be logged in!')
        return redirect(url_for('home'))

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
    user_id = cursor.fetchone()['id']

    cursor.execute("SELECT COUNT(*) AS total FROM recipes WHERE author=%s", (user_id,))
    number_of_my_rec = cursor.fetchone()['total']

    limit_per_page = 8
    current_page = int(request.args.get('current_page', 1))
    pages = range(1, int(math.ceil(number_of_my_rec / limit_per_page)) + 1)

    cursor.execute("""
        SELECT * FROM recipes WHERE author=%s
        ORDER BY id ASC
        LIMIT %s OFFSET %s
    """, (user_id, limit_per_page, (current_page - 1) * limit_per_page))
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("my_recipes.html",
                           username=username,
                           recipes=recipes,
                           number_of_my_rec=number_of_my_rec,
                           current_page=current_page,
                           pages=pages,
                           title='My Recipes')


# ------------------------------------------------
# ADD RECIPE
# ------------------------------------------------
@app.route('/add_recipe')
def add_recipe():
    if 'username' not in session:
        flash('You must be logged in to add a recipe!')
        return redirect(url_for('home'))

    form = Add_RecipeForm()

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM diets")
    diet_types = cursor.fetchall()

    cursor.execute("SELECT * FROM meals")
    meal_types = cursor.fetchall()

    cursor.execute("SELECT * FROM cuisines")
    cuisine_types = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("add_recipe.html",
                           diet_types=diet_types,
                           cuisine_types=cuisine_types,
                           meal_types=meal_types,
                           form=form,
                           title='New Recipe')


# ------------------------------------------------
# INSERT RECIPE
# ------------------------------------------------
@app.route("/insert_recipe", methods=['POST'])
def insert_recipe():
    if request.method == 'POST':

        ingredients = json.dumps(request.form.get("ingredients").splitlines())
        directions = json.dumps(request.form.get("recipe_directions").splitlines())

        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE username=%s", (session["username"],))
        author_id = cursor.fetchone()['id']

        cursor.execute("""
            INSERT INTO recipes (
                recipe_name, description, cuisine_type, meal_type,
                diet_type, cooking_time, servings, ingredients, directions,
                author, image
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form.get("recipe_name").strip(),
            request.form.get("recipe_description"),
            request.form.get("cuisine_type"),
            request.form.get("meal_type"),
            request.form.get("diet_type"),
            request.form.get("cooking_time"),
            request.form.get("servings"),
            ingredients,
            directions,
            author_id,
            request.form.get("image"),
        ))

        conn.commit()
        recipe_id = cursor.lastrowid

        cursor.close()
        conn.close()

        flash("Recipe added successfully!")
        return redirect(url_for("single_recipe_details", recipe_id=recipe_id))


# ------------------------------------------------
# EDIT RECIPE
# ------------------------------------------------
@app.route("/edit_recipe/<recipe_id>")
def edit_recipe(recipe_id):
    if 'username' not in session:
        flash("You must be logged in to edit recipes!")
        return redirect(url_for("home"))

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
    user_id = cursor.fetchone()['id']

    cursor.execute("SELECT * FROM recipes WHERE id=%s", (recipe_id,))
    selected_recipe = cursor.fetchone()

    if selected_recipe['author'] != user_id:
        flash("You can only edit your own recipes!")
        return redirect(url_for('home'))

    cursor.execute("SELECT * FROM diets")
    diet_types = cursor.fetchall()

    cursor.execute("SELECT * FROM meals")
    meal_types = cursor.fetchall()

    cursor.execute("SELECT * FROM cuisines")
    cuisine_types = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_recipe.html",
                           selected_recipe=selected_recipe,
                           diet_types=diet_types,
                           meal_types=meal_types,
                           cuisine_types=cuisine_types,
                           title='Edit Recipe')


# ------------------------------------------------
# UPDATE RECIPE
# ------------------------------------------------
@app.route("/update_recipe/<recipe_id>", methods=["POST"])
def update_recipe(recipe_id):
    conn = get_conn()
    cursor = conn.cursor()

    ingredients = json.dumps(request.form.get("ingredients").splitlines())
    directions = json.dumps(request.form.get("directions").splitlines())

    cursor.execute("""
        UPDATE recipes SET
            recipe_name=%s,
            description=%s,
            cuisine_type=%s,
            meal_type=%s,
            cooking_time=%s,
            diet_type=%s,
            servings=%s,
            ingredients=%s,
            directions=%s,
            image=%s
        WHERE id=%s
    """, (
        request.form.get("recipe_name"),
        request.form.get("recipe_description"),
        request.form.get("cuisine_type"),
        request.form.get("meal_type"),
        request.form.get("cooking_time"),
        request.form.get("diet_type"),
        request.form.get("servings"),
        ingredients,
        directions,
        request.form.get("recipe_image"),
        recipe_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("single_recipe_details", recipe_id=recipe_id))


# ------------------------------------------------
# DELETE RECIPE
# ------------------------------------------------
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    if 'username' not in session:
        flash("You must be logged in!")
        return redirect(url_for("home"))

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE username=%s", (session['username'],))
    user_id = cursor.fetchone()['id']

    cursor.execute("SELECT author FROM recipes WHERE id=%s", (recipe_id,))
    author = cursor.fetchone()['author']

    if author != user_id:
        flash("You can only delete your own recipes!")
        return redirect(url_for("home"))

    cursor.execute("DELETE FROM recipes WHERE id=%s", (recipe_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Recipe deleted.")
    return redirect(url_for("home"))


# ------------------------------------------------
# LOGIN
# ------------------------------------------------
@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        flash("Already logged in!")
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s",
                       (request.form['username'],))
        registered_user = cursor.fetchone()

        if registered_user and check_password_hash(registered_user['password'],
                                                  request.form['password']):
            session['username'] = registered_user['username']
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Incorrect username or password")

        cursor.close()
        conn.close()

    return render_template('login.html', form=form, title='Login')


# ------------------------------------------------
# REGISTER
# ------------------------------------------------
@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'username' in session:
        flash("Already registered!")
        return redirect(url_for('home'))

    form = RegisterForm()

    if form.validate_on_submit():
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s",
                       (request.form['username'],))
        registered_user = cursor.fetchone()

        if registered_user:
            flash("Username already taken!")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(request.form['password'])

        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (%s,%s)
        """, (request.form['username'], hashed_password))
        conn.commit()

        session['username'] = request.form['username']
        flash("Account created!")

        cursor.close()
        conn.close()

        return redirect(url_for('home'))

    return render_template('register.html', form=form, title='Register')


# ------------------------------------------------
# LOGOUT
# ------------------------------------------------
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


# ------------------------------------------------
# ACCOUNT SETTINGS
# ------------------------------------------------
@app.route("/account_settings/<username>")
def account_settings(username):
    if 'username' not in session:
        flash("Login required!")
        return redirect(url_for("home"))

    return render_template("account_settings.html",
                           username=session['username'],
                           title="Account Settings")


# ------------------------------------------------
# CHANGE USERNAME
# ------------------------------------------------
@app.route("/change_username/<username>", methods=["GET", "POST"])
def change_username(username):
    if 'username' not in session:
        flash("Login required!")
        return redirect(url_for("home"))

    form = ChangeUsernameForm()

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    if form.validate_on_submit():

        cursor.execute("SELECT * FROM users WHERE username=%s",
                       (request.form['new_username'],))
        exists = cursor.fetchone()
        if exists:
            flash("Username already taken!")
            return redirect(url_for('change_username', username=username))

        cursor.execute("""
            UPDATE users SET username=%s WHERE username=%s
        """, (request.form['new_username'], username))
        conn.commit()

        cursor.close()
        conn.close()

        session.pop("username", None)
        flash("Username updated. Please login again.")
        return redirect(url_for("login"))

    return render_template("change_username.html",
                           form=form,
                           username=username,
                           title="Change Username")


# ------------------------------------------------
# CHANGE PASSWORD
# ------------------------------------------------
@app.route("/change_password/<username>", methods=["GET", "POST"])
def change_password(username):
    if 'username' not in session:
        flash("Login required!")
        return redirect(url_for("home"))

    form = ChangePasswordForm()

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if form.validate_on_submit():
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        confirm = request.form.get("confirm_new_password")

        if not check_password_hash(user['password'], old):
            flash("Incorrect old password!")
            return redirect(url_for('change_password', username=username))

        if new != confirm:
            flash("New passwords do not match!")
            return redirect(url_for('change_password', username=username))

        cursor.execute("""
            UPDATE users SET password=%s WHERE username=%s
        """, (generate_password_hash(new), username))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Password updated!")
        return redirect(url_for('account_settings', username=username))

    return render_template("change_password.html",
                           form=form,
                           username=username,
                           title="Change Password")


# ------------------------------------------------
# DELETE ACCOUNT
# ------------------------------------------------
@app.route("/delete_account/<username>", methods=["POST"])
def delete_account(username):
    if "username" not in session:
        flash("Login required!")
        return redirect(url_for("home"))

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if not check_password_hash(
        user["password"], request.form.get("confirm_password_to_delete")
    ):
        flash("Incorrect password!")
        return redirect(url_for("account_settings", username=username))

    cursor.execute("DELETE FROM recipes WHERE author=%s", (user["id"],))
    cursor.execute("DELETE FROM users WHERE id=%s", (user["id"],))
    conn.commit()

    cursor.close()
    conn.close()

    session.pop("username", None)
    flash("Account deleted.")
    return redirect(url_for("home"))


# ------------------------------------------------
# SEARCH (SQL VERSION)
# ------------------------------------------------
@app.route("/search")
def search():
    query = request.args.get("query", "")
    limit_per_page = 8
    current_page = int(request.args.get('current_page', 1))

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    search_sql = """
        SELECT * FROM recipes
        WHERE recipe_name LIKE %s OR description LIKE %s
        ORDER BY id ASC
        LIMIT %s OFFSET %s
    """

    like = f"%{query}%"

    cursor.execute("SELECT COUNT(*) AS total FROM recipes WHERE recipe_name LIKE %s OR description LIKE %s",
                   (like, like))
    total = cursor.fetchone()['total']

    cursor.execute(search_sql, (like, like, limit_per_page, (current_page - 1) * limit_per_page))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    pages = range(1, int(math.ceil(total / limit_per_page)) + 1)

    return render_template(
        "search.html",
        title="Search",
        query=query,
        results=results,
        number_of_recipes_found=total,
        current_page=current_page,
        results_pages=pages,
        total_pages=len(pages)
    )

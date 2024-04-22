from db import DB
from flask import Flask, redirect, render_template, session, request
from login_form import LoginForm
from users_model import UsersModel
from register_form import RegisterModel
from units_model import UnitsModel
from units_form import UnitForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
db = DB()
UsersModel(db.get_connection()).init_table()
flag_perm = False
image = []

cur = UsersModel(db.get_connection())
admins = dict(cur.get("username, password_hash", "WHERE is_admin = 1").fetchall())


def make_session_permanent():
    session.permanent = False


def generate_hash(string):
    p = 97
    m = 10 ** 9 + 9
    string += "w1T!g=z%1S#93H%"

    char_hash = {chr(i): i for i in range(32, 123)}
    hash_ = 0
    for i in range(len(string)):
        hash_ += (char_hash[string[i]] * p ** i) % m

    return hash_


@app.route("/register", methods=["POST", "GET"])
def register():
    if "username" in session:
        return redirect("/")
    form = RegisterModel()
    if form.validate_on_submit():
        username = form.username.data
        password_hash = generate_hash(form.password.data)
        user = UsersModel(db.get_connection())
        flag = user.exists(username)
        if flag and username not in admins:
            user.insert(username, password_hash)
            session["username"] = username
            exists = user.exists(username, password_hash)
            session["user_id"] = exists[1]
            return redirect("/")
        else:
            return render_template("register.html", form=form, error=1)
    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    global flag_perm
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password_hash = generate_hash(form.password.data)
        perm = form.remember_button.data

        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(username, password_hash)

        if exists[0]:
            session["username"] = username
            session["user_id"] = exists[1]
            if perm:
                session.permanent = True
                flag_perm = True
            else:
                session.permanent = False
                flag_perm = True
            return redirect("/index")
        else:
            return render_template("login.html", form=form, error=1)
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", 0)
    session.pop("user_id", 0)
    return redirect("/login")


@app.route("/index")
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "GET":
        if "username" not in session or not flag_perm and not session.permanent:
            if "username" in session:
                return redirect("/logout")
            return redirect("/login")
        user_model = UsersModel(db.get_connection())
        all_users = user_model.get_all()
        if session["username"] in admins:
            return render_template("index.html", admins=admins, username=session["username"], all_users=all_users)
        return render_template("index.html", username=session["username"], admins=admins)


@app.route("/site_users", methods=["GET"])
def site_users():
    if "username" not in session:
        return redirect("/login")
    if session["username"] not in admins:
        return redirect("/")
    user_model = UsersModel(db.get_connection())
    num = user_model.get_all()
    all_users = []
    for i in num:
        id_ = i[0]
        username = i[1]
        password = i[2]
        all_users.append((id_, username, password))
    return render_template("site_users.html", users=all_users, admins=admins, username=session["username"])


@app.route("/delete_unit/<int:unit_id>", methods=["GET"])
def delete_unit(unit_id):
    if "username" not in session:
        return redirect("/login")
    units_model_ = UnitsModel(db.get_connection())
    units_model_.delete(unit_id)
    return redirect("/all_units")


@app.route("/all_units", methods=["GET"])
def all_units():
    units_model_ = UnitsModel(db.get_connection())
    units = units_model_.get_all()
    if session["username"] in admins:
        return render_template("all_units.html", show=1, units=units, username=session["username"], admins=admins)
    else:
        return render_template("all_units.html", units=units, username=session["username"], admins=admins)


@app.route("/add_unit_image")
def upload_files():
    if "username" not in session:
        return redirect("/")
    return render_template("add_unit_image.html", show=1)


@app.route("/add_unit_extra", methods=["POST", "GET"])
def add_unit_extra():
    if "username" not in session:
        return redirect("/")
    form = UnitForm()
    image_name = image[-1]
    if form.validate_on_submit():
        name = form.name.data
        content_ = form.content.data
        cost = form.cost.data
        units = UnitsModel(db.get_connection())
        flag = units.exists(name)
        if not flag:
            units.insert(image_name, name, content_, cost)
            return redirect("/all_units")
        else:
            return render_template("add_unit_extra.html", form=form, error=1)
    return render_template("add_unit_extra.html", form=form)


@app.route("/upload", methods=["POST", "GET"])
def upload():
    if "username" not in session:
        return redirect("/")
    if request.method == "POST":
        f = request.files["file"]
        hash_ = str(generate_hash(f.filename)) + "." + f.filename.split(".")[1]
        f.save(f"static/{hash_}")
        img_name = f"/static/{hash_}"
        image.append(img_name)
        return redirect("/add_unit_extra")


@app.route("/add_in_cart/<int:unit_id>", methods=["GET"])
def add_in_cart(unit_id):
    if "username" not in session:
        return redirect("/")

    users_model = UsersModel(db.get_connection())
    user_id = session["user_id"]
    cart_ = users_model.get("cart", f"WHERE id = {user_id}").fetchone()[0]
    if cart_ is not None:
        cart_ += f" {unit_id}"
        cart_ = " ".join(set(cart_.split()))
    else:
        cart_ = f"{unit_id}"
    users_model.other_commands(f'UPDATE users SET cart = "{cart_}" WHERE id = {user_id}')

    return redirect("/cart")


@app.route("/del_from_cart/<int:unit_id>", methods=["GET"])
def del_from_cart(unit_id):
    if "username" not in session:
        return redirect("/")

    users_model = UsersModel(db.get_connection())
    user_id = session["user_id"]
    cart_ = users_model.get("cart", f"WHERE id = {user_id}").fetchone()[0]
    if cart_ is not None:
        cart_ = cart_.split()
        if str(unit_id) in cart_:
            cart_.remove(str(unit_id))
        cart_ = " ".join(cart_)
    users_model.other_commands(f'UPDATE users SET cart = "{cart_}" WHERE id = {user_id}')

    return redirect("/cart")


@app.route("/cart", methods=["GET"])
def cart():
    if "username" not in session:
        return redirect("/")
    users_model = UsersModel(db.get_connection())
    units_model = UnitsModel(db.get_connection())
    cart_ = users_model.get("cart", f"WHERE id = {session['user_id']}").fetchone()[0]
    text = []
    if cart_ is not None:
        for i in cart_.split():
            text.append(*units_model.get("*", f"WHERE id = {i}").fetchall())
    return render_template("cart.html", units=text)


if __name__ == "__main__":
    # from waitress import serve
    # serve(app, port=8080, host="127.0.0.1")

    app.run(port=8080, host="127.0.0.1")

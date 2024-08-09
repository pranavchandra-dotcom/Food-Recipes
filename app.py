"""Frame work for the website"""
import logging
import os
import platform
from datetime import datetime
from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
myhost = platform.node()
app = Flask(__name__)
picture_folder = os.path.join("static", "pictures")
app.config["UPLOAD_FOLDER"] = picture_folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "thisissecretkey"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
log_format_dt = datetime.utcnow().date().isoformat()
logger = logging.basicConfig(
     level=logging.DEBUG,
     format="{asctime} {myhost}: {message}",
     style='{',
     datefmt="%m/%d/%Y %I:%M:%S %p",
     filename=f"logs/log_{log_format_dt}.log",
     filemode="w",

 )


def password_check(password):
    """Password Checker"""
    special_sym = ["$", "@", "#", "%", ""]
    val = True
    if len(password) < 12:
        val = False
    if len(password) > 20:
        val = False
    if not any(char.isdigit() for char in password):
        val = False
    if not any(char.isupper() for char in password):
        val = False
    if not any(char.islower() for char in password):
        val = False
    if not any(char in special_sym for char in password):
        val = False
    if val:
        return val
    return None


def password_reset_conditions(password):
    """function for validating new passoword."""
    with open("CommonPassword.txt", "r", encoding="utf-8") as in_file:
        common_passwords = in_file.readlines()
    password_in_common_passwords = True if password not in common_passwords else False
    password_check_value = password_check(password)
    return all([password_in_common_passwords, password_check_value])


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """Loading the User"""
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """Table model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    """Class for Registration"""

    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )

    password = PasswordField(
        validators=[InputRequired(), Length(min=12, max=20)],
        render_kw={"placeholder": "Password"},
    )

    submit = SubmitField("Register")

    def validate_username(self, username):
        """Validating the username"""
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one."
            )


class LoginForm(FlaskForm):
    """Class for Login form"""

    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )

    password = PasswordField(
        validators=[InputRequired(), Length(min=12, max=20)],
        render_kw={"placeholder": "Password"},
    )

    submit = SubmitField("Login")


class PasswordResetForm(FlaskForm):
    """Password Reset link"""

    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )

    current_password = PasswordField(
        validators=[InputRequired(), Length(min=12, max=20)],
        render_kw={"placeholder": "Current Password"},
    )
    new_password = PasswordField(
        validators=[InputRequired(), Length(min=12, max=20)],
        render_kw={"placeholder": "New Password"},
    )
    confirm_password = PasswordField(
        validators=[InputRequired(), Length(min=12, max=20)],
        render_kw={"placeholder": "Confirm Password"},
    )

    submit = SubmitField("Reset")


def get_datetime_now():
    """Fuction for date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route("/", methods=["POST", "GET"])
def login():
    """Function for Login"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("main"))
        else:
             logger.error("Login Unsuccessfull")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Function for Logout"""
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["POST", "GET"])
def register():
    """Function for Registration"""
    form = RegisterForm()
    if form.validate_on_submit():
        if password_check(form.password.data):
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("main"))
        flash("Password not strong enough.")
        return redirect(url_for("register"))
    return render_template("register.html", form=form)


@app.route("/passwordreset", methods=["POST", "GET"])
def password_reset():
    """Funtion for resetting password."""
    form = PasswordResetForm()
    user = User.query.filter_by(username=form.username.data).first()
    if form.validate_on_submit():
        if password_reset_conditions(form.new_password.data):
            if bcrypt.check_password_hash(user.password, form.current_password.data):
                hashed_password = bcrypt.generate_password_hash(form.new_password.data)
                user.password = hashed_password
                db.session.commit()
                return redirect(url_for("login"))
            flash("Enter the correct old password...")
        flash(
            "New Password not following security recommendations. Please enter a valid password"
        )

    return render_template("resetpassword.html", form=form)


@app.route("/main")
def main():
    """Function for main"""
    recipe1 = "Jack Fruit Biryani"
    recipe2 = "Dal Makhni"
    recipe3 = "Chicken Curry "
    jack_fruit = os.path.join(app.config["UPLOAD_FOLDER"], "jackfruit.png")
    dal = os.path.join(app.config["UPLOAD_FOLDER"], "dalmakhni.png")
    chicken = os.path.join(app.config["UPLOAD_FOLDER"], "chickencurry.png")
    return render_template(
        "main.html",
        recipea=recipe1,
        recipeb=recipe2,
        recipec=recipe3,
        picture1=jack_fruit,
        picture2=dal,
        picture3=chicken,
    )


@app.route("/jackfruitbiryani", methods=["POST", "GET"])
def jack_fruit_biryani():
    """Function for recipe 1"""
    jack_fruit = os.path.join(app.config["UPLOAD_FOLDER"], "jackfruit.png")
    title = "Jack Fruit Biryani"
    ingredients = [
        "2 x 400g tins jackfruit (about 450g drained weight)",
        "10g garlic paste",
        "10g ginger paste",
        "½ tsp fine sea salt",
        "¼ tsp ground turmeric",
        "½ tsp deggi mirch chilli powder",
        "Vegetable oil for deep-frying",
        "150g baby new potatoes",
        "250 vegetable oil",
        "2 crispy fried onions, sliced into half-moons (fry in 250ml vegetable oil for 15 minutes)",
        "10g garlic paste",
        "10g ginger paste",
        "1 tsp fine sea salt",
        " 1 tsp deggi mirch chilli powder",
        "1½ tsp ground cumin",
        " ¼ tsp garam masala",
        "20ml lime juice",
        "150g full-fat Greek yoghurt",
        "2 green chillies, sliced into strips",
        "3cm fresh root ginger, cut into fine matchsticks",
        "6 mint leaves, roughly chopped",
        "25 coriander leaves",
        "30g sultanas",
        "30g butter",
        "3 tbsp double cream",
        "1 large pinch saffron, toasted, cooled, mixed in 2 tbsp boiling water",
    ]
    recipe = """ First, soak the rice. Put the rice into a large bowl and cover generously
                with water.
                Using your fingers,
                gently move the rice around in the water to remove the starch, being careful not to break up the grains. 
                Let the rice settle, then pour off the water. Repeat twice more, each time with fresh water, then cover again with fresh water and leave to soak for 45 minutes.
                To prepare the jackfruit, pat dry with kitchen paper and cut the larger pieces in half. In a large bowl, combine the garlic and ginger pastes with the salt, turmeric, 
                chilli powder and a tablespoon of water, 
                then coat the jackfruit in this mixture and leave to marinate for 30 minutes.
                Cut the potatoes into bite-sized pieces, add to a pan of boiling, salted water and cook until almost tender. Drain and pat dry, then set aside.
                Heat the oven to 200C (180C fan)/gas 6. Heat the oil in a deep-fryer or other suitable deep, heavy-based pan to 170C/335F. Deep-fry the marinated jackfruit in the hot oil, in two batches, 
                if necessary, until golden brown and crisp all over – this will take about 10 minutes – then drain on kitchen paper. 
                Add the drained potatoes to the hot oil, fry for five minutes, then drain on kitchen paper.
                Combine all of the biryani base ingredients, including the fried potatoes, in a biryani cooking pot, add the jackfruit and stir to combine. Set aside."
                Drain the rice when the soaking time is up. Pour two litres of boiling water into a large pan and add the two teaspoons of salt and the lime juice. Tip the rice into the pan and stir well. 
                Boil until it is three-quarters cooked, which should take four minutes from the time the rice went into the pan – 
                you can tell that it’s at this stage by taking a grain between your forefinger and thumb, and pressing down on it with your nail:
                it should still be slightly firm and break into five or six pieces. Drain the rice; you don’t need to shake it completely dry, because a little extra moisture helps during cooking. 
                Add the rice to the biryani, spreading it out on top of the jackfruit, and scatter with sultanas.
                In a small pan, or very quickly in the microwave, warm the butter and cream until the butter melts, then trickle this and the saffron water on to the rice. Cover tightly with two layers of foil and a lid, 
                put on a high heat for two to three minutes, until you hear the marinade start to sizzle, 
                then transfer to the oven and bake for 20 minutes. Leave the biryani to stand, still covered, for 10 minutes before serving.
    """
    return render_template(
        "recipes.html",
        titles=title,
        ingredient=ingredients,
        recipes=recipe,
        datetime=get_datetime_now(),
        picture=jack_fruit,
    )


@app.route("/dalmakhni", methods=["POST"])
def dal_makni():
    """Function for Recipe 2"""
    dal = os.path.join(app.config["UPLOAD_FOLDER"], "dalmakhni.png")
    title = "Dal Makhni"
    ingredients = [
        "300g urad dal",
        "4 litres cold water",
        "12g garlic paste",
        "10g ginger paste",
        "70g tomato puree",
        "8g fine sea salt",
        "⅔ tsp deggi mirch chilli powder",
        "⅓ tsp garam masala",
        "90g unsalted butter",
        "90ml double cream",
        "Chapatis, to serve",
    ]
    recipe = """But the dal into a large bowl, cover with water and whisk for 10 seconds.
                Let the dal settle, then pour out the water.
                Repeat three or four times, 
                until the water is clear. Tip the dal into a large saucepan and pour in at least four litres of cold water. 
                Bring to a boil and cook steadily for two to three hours. 
                Skim off any impurities that rise to the surface, and add more boiling water as required to keep the grains well covered. 
                The dal grains need to become completely soft, 
                with the skins coming away from the white grain. When pressed, the white part should be creamy, rather than crumbly. When cooked, 
                turn off the heat and set aside for 15 minutes.
                In a bowl, mix the garlic and ginger pastes, tomato puree, salt, chilli powder and garam masala into a paste.
                Carefully pour off the dal cooking water, then pour on enough freshly boiled water to cover the dal by 3-4cm. 
                Bring to a boil over a medium-high heat, then add the aromatic paste and butter. 
                Cook rapidly for 30 minutes, stirring regularly to prevent the mixture from sticking.
                Lower the heat and simmer for one to one and a half hours more, stirring regularly to prevent it from sticking, 
                and adding a little boiling water if the liquid level gets near the level of the grains. 
                Eventually, the dal will turn thick and creamy. The creaminess must come from the grains disintegrating into the liquid and enriching it, 
                not from the water being allowed to evaporate, leaving only the grains behind.
                Add the cream and cook for a further 15 minutes. Serve with chapatis or other Indian breads. 
                When reheating any leftover dal, you may need to add a little more liquid; use cream or cream and water, rather than just water alone."""
    return render_template(
        "recipes.html",
        titles=title,
        ingredient=ingredients,
        recipes=recipe,
        datetime=get_datetime_now(),
        picture=dal,
    )


@app.route("/chicken_curry", methods=["POST"])
def chicken_curry():
    """Function for recipe 3"""
    chicken = os.path.join(app.config["UPLOAD_FOLDER"], "chickencurry.png")
    title = "Chicken Curry"
    ingredients = [
        "700g skinless, boneless chicken thighs",
        "20g unsalted butter, melted",
        "50ml double cream",
        "For the makhani sauce",
        "35g garlic (7–8 cloves)",
        "175ml vegetable oil",
        "20g fresh root ginger",
        "800g chopped tomatoes (fresh or good-quality tinned)",
        "2 bay leaves",
        "6 green cardamom pods",
        "2 black cardamom pods",
        "2 cinnamon sticks",
        "2 tsp fine sea salt",
        "1½ tsp deggi mirch chilli powder",
        "30g butter",
        "1 tsp garam masala",
        "20g granulated sugar",
        "1 tbsp runny honey",
        "1 tsp ground cumin",
        "1 tsp kasoori methi powder, crushed to a powder between your fingers",
        "½ tsp fresh dill fronds",
        "80ml double cream",
        "Advertisement" "For the marinade",
        "10g chopped fresh ginger",
        "20g chopped garlic" "5g fine sea salt" "1 tsp deggi mirch chilli powder",
        "1½ tsp ground cumin",
        "½ tsp garam masala",
        "2 tsp lime juice",
        "2 tsp vegetable oil",
        "75g full-fat greek yoghurt",
        "For the garnish",
        "Ginger matchsticks",
        "Coriander leaves, chopped",
        "1 tbsp pomegranate seeds",
    ]
    recipe = {
        """First make the makhani sauce. Peel and finely dice 15g of the garlic.
    Warm a large saucepan over a medium-high heat and add the oil. 
            Toss in the chopped garlic and fry until light golden brown and slightly crisp – about seven to eight minutes. 
            Remove with a slotted spoon and drain on kitchen paper.
            Grate the remaining garlic and the ginger to a fine paste on a microplane (or grind in a mortar). 
            Using a blender, blitz the chopped tomatoes to a fine consistency.
            Put the saucepan containing the oil back on a medium-high heat and add the bay leaves, green and black cardamom pods, 
            and the cinnamon sticks. 
            Let them crackle for one minute, stirring regularly, 
            then turn down the heat and add the garlic and ginger paste. Cook for five minutes, allowing the paste to brown but not burn.
            Add the tomatoes, salt and chilli powder to the pan. Bring to a rapid simmer and cook until reduced by half, 
            stirring regularly so it doesn’t catch – this should take about 30 minutes. 
            Add the butter and simmer for a further five minutes. Add the garam masala, sugar, honey, cumin, crisp garlic, 
            kasoori methi powder and dill fronds, and cook for a further 15 minutes. 
            Add the cream and simmer gently for five minutes. The sauce is now ready to use.
            For the marinade, blitz all the ingredients to a smooth paste, then transfer to a bowl. 
            Cut the chicken into 4cm chunks, add to the marinade and turn to coat. 
            Cover and leave to marinate in the fridge for six to 24 hours.
            Heat the grill to medium-high. Put the marinated chicken on a rack in the grill pan, 
            brush with the melted butter and grill for eight to 10 minutes, until cooked through and nicely charred.
            To finish, warm a large saucepan over a medium-low heat. Add the makhani sauce, 
            cream and grilled chicken, and simmer very gently for 10 minutes. Serve the curry garnished with ginger matchsticks, 
            chopped coriander and pomegranate seeds, with a bowl of steamed rice on the side."""
    }
    return render_template(
        "recipes.html",
        titles=title,
        ingredient=ingredients,
        recipes=recipe,
        datetime=get_datetime_now(),
        picture=chicken,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

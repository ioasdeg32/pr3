from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class UnitForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    content = TextAreaField("Описание", validators=[DataRequired()])
    cost = IntegerField("Цена", validators=[DataRequired()])
    submit = SubmitField("Добавить")

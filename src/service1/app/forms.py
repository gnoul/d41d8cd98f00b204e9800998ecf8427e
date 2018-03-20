from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class GraphForm(FlaskForm):
    formula = StringField('formula', validators=[DataRequired()])
    period = StringField('period', validators=[DataRequired()], default='2d')
    step = StringField('step', validators=[DataRequired()], default='3h')


# TODO: Валидатор для period и step
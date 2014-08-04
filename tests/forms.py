from wtforms import Form, TextField
from wtforms.validators import InputRequired, ValidationError

class SimpleForm(Form):
    """ The basic test form. """
    first_name = TextField("First name", validators=[InputRequired()])
    last_name = TextField("Last name", validators=[InputRequired()])

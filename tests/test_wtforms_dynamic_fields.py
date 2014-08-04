import pytest
from copy import deepcopy
from forms import SimpleForm
from webob.multidict import MultiDict
from wtforms import TextField
from wtforms.validators import InputRequired
from wtforms_dynamic_fields.wtforms_dynamic_fields import WTFormsDynamicFields

""" This test module uses PyTest (py.test command) for its testing. """

@pytest.fixture(scope="module")
def setup(request):
    """ Initiate the basic POST mockup. """
    post = MultiDict()
    post.add(u'first_name',u'John')
    post.add(u'last_name',u'Doe')
    return post

# Below follow the actual tests

def test_add_single_field_without_validation(setup):
    post = deepcopy(setup)
    post.add(u'email', '')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    form = dynamic_form.process(SimpleForm,
                                post)

    # Is the HTML what we expect?
    assert form.email() == '<input id="email" name="email" type="text" value="">'
    # Is the label correct?
    assert form.email.label.text == 'Email'

def test_add_single_field_with_validation_error(setup):
    post = deepcopy(setup)
    post.add(u'email', '')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator('email', InputRequired)
    form = dynamic_form.process(SimpleForm,
                                post)
    
    assert form.validate() == False
    assert form.errors['email'] == ['This field is required.']

def test_add_single_field_with_validation_success(setup):
    post = deepcopy(setup)
    post.add(u'email', 'foo')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator(name='email', validator=InputRequired)
    form = dynamic_form.process(SimpleForm,
                                post)
    
    assert form.validate() == True


def test_sets_of_single_fields(setup):
    post = deepcopy(setup)
    post.add(u'email_1', 'one@mail.mock')
    post.add(u'email_2', 'two@mail.mock')
    post.add(u'email_3', 'three@mail.mock')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator('email', InputRequired, 'foo', 'faa')
    form = dynamic_form.process(SimpleForm,
                                post)

    assert form.validate() == True
    assert form.email_1.data == 'one@mail.mock'
    assert form.email_2.data == 'two@mail.mock'
    assert form.email_3.data == 'three@mail.mock'


def test_sets_of_multiple_single_fields(setup):
    post = deepcopy(setup)
    post.add(u'email_1', 'one@mail.mock')
    post.add(u'email_2', 'two@mail.mock')
    post.add(u'email_3', 'three@mail.mock')
    post.add(u'telephone_1', '14564678')
    post.add(u'telephone_2', '64578952')
    post.add(u'telephone_3', '31794561')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_field('telephone','Telephone', TextField)
    dynamic_form.add_validator('email', InputRequired)
    dynamic_form.add_validator('telephone', InputRequired)
    form = dynamic_form.process(SimpleForm,
                                post)

    assert form.validate() == True
    assert form.email_1.data == 'one@mail.mock'
    assert form.email_2.data == 'two@mail.mock'
    assert form.email_3.data == 'three@mail.mock'
    assert form.telephone_1.data == '14564678'
    assert form.telephone_2.data == '64578952'
    assert form.telephone_3.data == '31794561'

def test_automatic_label_suffix(setup):
    post = deepcopy(setup)
    post.add(u'email_1', '')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator('email', InputRequired, message='Please fill in %email%.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()

    assert form.errors['email_1'] == ['Please fill in email_1.']

def test_dependend_automatic_label_suffix(setup):
    post = deepcopy(setup)
    post.add(u'email_1', '')
    post.add(u'telephone_1', '')
    post.add(u'pager_1', '')
    post.add(u'email_2', '')
    post.add(u'telephone_2', '')
    post.add(u'pager_2', '')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator('email', InputRequired, message='Please fill in %telephone% or %pager%.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()

    assert form.errors['email_1'] == ['Please fill in telephone_1 or pager_1.']
    assert form.errors['email_2'] == ['Please fill in telephone_2 or pager_2.']

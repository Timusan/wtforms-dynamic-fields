from __future__ import absolute_import
import pytest
from copy import deepcopy
from .forms import SimpleForm
from webob.multidict import MultiDict
from wtforms import TextField
from wtforms.validators import InputRequired
from wtforms_dynamic_fields import WTFormsDynamicFields

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
    """ Test correct re-injection of single field by WTForms
    No sets - No error situation.
    Fields email has no validator and this is invalid.
    It should be present after validation.
    """
    post = deepcopy(setup)
    post.add(u'email', '')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    form = dynamic_form.process(SimpleForm,
                                post)

    assert form.email() == '<input id="email" name="email" type="text" value="">'
    assert form.email.label.text == 'Email'

def test_add_single_field_with_validation_error(setup):
    """ Test correct re-injection of single field by WTForms
    No sets - Error situation.
    Fields email is invalid thus should trigger an error
    after validation and be present in the form.
    """
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
    """ Test correct re-injection of single field by WTForms
    No sets - No error situation.
    Fields email is valid and should be present in the form
    after validation.
    """
    post = deepcopy(setup)
    post.add(u'email', 'foo')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator('email', InputRequired)
    form = dynamic_form.process(SimpleForm,
                                post)
    
    assert form.validate() == True
    assert form.email() == '<input id="email" name="email" type="text" value="foo">'

def test_sets_of_single_fields(setup):
    """ Test correct re-injection of multiple fields by WTForms
    Sets - No error situation.
    Fields email_x are valid and should be present in
    the form after validation.
    """
    post = deepcopy(setup)
    post.add(u'email_1', 'one@mail.mock')
    post.add(u'email_2', 'two@mail.mock')
    post.add(u'email_3', 'three@mail.mock')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator('email', InputRequired)
    form = dynamic_form.process(SimpleForm,
                                post)

    assert form.validate() == True
    assert form.email_1.data == 'one@mail.mock'
    assert form.email_2.data == 'two@mail.mock'
    assert form.email_3.data == 'three@mail.mock'
    assert form.email_1() == '<input id="email_1" name="email_1" type="text" value="one@mail.mock">'
    assert form.email_2() == '<input id="email_2" name="email_2" type="text" value="two@mail.mock">'
    assert form.email_3() == '<input id="email_3" name="email_3" type="text" value="three@mail.mock">'


def test_sets_of_multiple_single_fields(setup):
    """ Test correct re-injection of multiple sets by WTForms
    Sets - No error situation.
    Fields email_x and telephone_x are valid and should be
    present in the form after validation.
    """
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
    assert form.email_1() == '<input id="email_1" name="email_1" type="text" value="one@mail.mock">'
    assert form.email_2() == '<input id="email_2" name="email_2" type="text" value="two@mail.mock">'
    assert form.email_3() == '<input id="email_3" name="email_3" type="text" value="three@mail.mock">'
    assert form.telephone_1.data == '14564678'
    assert form.telephone_2.data == '64578952'
    assert form.telephone_3.data == '31794561'
    assert form.telephone_1() == '<input id="telephone_1" name="telephone_1" type="text" value="14564678">'
    assert form.telephone_2() == '<input id="telephone_2" name="telephone_2" type="text" value="64578952">'
    assert form.telephone_3() == '<input id="telephone_3" name="telephone_3" type="text" value="31794561">'

def test_automatic_label_suffix(setup):
    """ Test %% replacement with single field
    Sets - Error situation.
    Fields email_x should not be blank.
    Merely inducing an error to assert for correct field name replacement.
    """
    post = deepcopy(setup)
    post.add(u'email_1', '')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('email','Email', TextField)
    dynamic_form.add_validator('email', InputRequired, message='Please fill in %email%.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()

    assert form.errors['email_1'] == ['Please fill in email_1.']
    assert form.email_1() == '<input id="email_1" name="email_1" type="text" value="">'

def test_dependend_automatic_label_suffix(setup):
    """ Test %% replacement with many fields
    Sets - Error situation.
    Fields email_x and telephone_x should not be blank.
    Merely inducing an error to assert for correct field name replacement.
    """
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
    assert form.email_1() == '<input id="email_1" name="email_1" type="text" value="">'
    assert form.email_2() == '<input id="email_2" name="email_2" type="text" value="">'

def test_long_field_name_replacement(setup):

    """ Test %% replacement with many fields
    Sets - Error situation.
    See if fields with many underscores and digits still
    get picked up correctly by the %field_name% formatter.
    Merely inducing an error to assert for correct field name replacement.
    """
    post = deepcopy(setup)
    post.add(u'a_very_long_10_field_name_1', '')
    post.add(u'yet_another_34_long_2_name_10_1', '')
    post.add(u'a_very_long_10_field_name_2', '')
    post.add(u'yet_another_34_long_2_name_10_2', '')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('a_very_long_10_field_name',
                           'A very long field name', TextField)
    dynamic_form.add_validator('a_very_long_10_field_name',
                               InputRequired,
                               message='Please fill in %a_very_long_10_field_name% or %yet_another_34_long_2_name_10%.')
    dynamic_form.add_field('yet_another_34_long_2_name_10',
                           'A very long field name', TextField)
    dynamic_form.add_validator('yet_another_34_long_2_name_10',
                               InputRequired,
                               message='Please fill in %a_very_long_10_field_name% or %yet_another_34_long_2_name_10%.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()

    assert form.validate() == False
    assert form.errors['a_very_long_10_field_name_1'] == ['Please fill in a_very_long_10_field_name_1 or yet_another_34_long_2_name_10_1.']
    assert form.errors['yet_another_34_long_2_name_10_1'] == ['Please fill in a_very_long_10_field_name_1 or yet_another_34_long_2_name_10_1.']
    assert form.errors['a_very_long_10_field_name_2'] == ['Please fill in a_very_long_10_field_name_2 or yet_another_34_long_2_name_10_2.']
    assert form.errors['yet_another_34_long_2_name_10_2'] == ['Please fill in a_very_long_10_field_name_2 or yet_another_34_long_2_name_10_2.']
    assert form.a_very_long_10_field_name_1() == '<input id="a_very_long_10_field_name_1" name="a_very_long_10_field_name_1" type="text" value="">'
    assert form.yet_another_34_long_2_name_10_1() == '<input id="yet_another_34_long_2_name_10_1" name="yet_another_34_long_2_name_10_1" type="text" value="">'
    assert form.a_very_long_10_field_name_2() == '<input id="a_very_long_10_field_name_2" name="a_very_long_10_field_name_2" type="text" value="">'
    assert form.yet_another_34_long_2_name_10_2() == '<input id="yet_another_34_long_2_name_10_2" name="yet_another_34_long_2_name_10_2" type="text" value="">'

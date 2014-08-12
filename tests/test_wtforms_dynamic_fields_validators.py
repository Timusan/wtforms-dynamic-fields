from __future__ import absolute_import
import pytest
from copy import deepcopy
from .forms import SimpleForm
from webob.multidict import MultiDict
from wtforms import TextField, IntegerField
from wtforms.validators import (EqualTo, Length, NumberRange, AnyOf)
from wtforms_dynamic_fields import WTFormsDynamicFields

""" This test module uses PyTest (py.test command) for its testing.

Testing behavior with different, built-in WTForms validators.
These tests mainly poke the validator argument binding and argument
%field_name% replacement.
"""

@pytest.fixture(scope="module")
def setup(request):
    """ Initiate the basic POST mockup. """
    post = MultiDict()
    post.add(u'first_name',u'John')
    post.add(u'last_name',u'Doe')
    return post

# Below follow the actual tests

def test_validator_equalto_error(setup):
    """ Test EqualTo validator
    No set - Error situation.
    Fields Mobile and Handy are not equal.
    """
    post = deepcopy(setup)
    post.add(u'mobile', '123456')
    post.add(u'handy', '654321')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('mobile','Mobile', TextField)
    dynamic_form.add_validator('mobile', EqualTo, 'handy', message='Please fill in the exact same data as handy.')
    dynamic_form.add_field('handy','Handy', TextField)
    dynamic_form.add_validator('handy', EqualTo, 'mobile', message='Please fill in the exact same data as mobile.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == False
    assert form.errors['mobile'] == ['Please fill in the exact same data as handy.']
    assert form.errors['handy'] == ['Please fill in the exact same data as mobile.']
    assert form.mobile() == '<input id="mobile" name="mobile" type="text" value="123456">'
    assert form.handy() == '<input id="handy" name="handy" type="text" value="654321">'

def test_validator_equalto_correct(setup):
    """ Test EqualTo validator
    No set - No error situation.
    Fields Mobile and Handy are equal.
    """
    post = deepcopy(setup)
    post.add(u'mobile', '123456')
    post.add(u'handy', '123456')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('mobile','Mobile', TextField)
    dynamic_form.add_validator('mobile', EqualTo, 'handy', message='Please fill in the exact same data as handy.')
    dynamic_form.add_field('handy','Handy', TextField)
    dynamic_form.add_validator('handy', EqualTo, 'mobile', message='Please fill in the exact same data as mobile.')
    form = dynamic_form.process(SimpleForm,
                                post)

    form.validate()
    assert form.validate() == True
    assert form.mobile() == '<input id="mobile" name="mobile" type="text" value="123456">'
    assert form.handy() == '<input id="handy" name="handy" type="text" value="123456">'

def test_validator_equalto_error_multiple(setup):
    """ Test EqualTo validator
    Multiple sets - Error situation.
    Note that only modile_2 and handy_2 are incorrect.
    """
    post = deepcopy(setup)
    post.add(u'mobile_1', '123456')
    post.add(u'handy_1', '123456')
    post.add(u'mobile_2', '456789')
    post.add(u'handy_2', '987654')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('mobile','Mobile', TextField)
    dynamic_form.add_validator('mobile', EqualTo, '%handy%', message='Please fill in the exact same data as %handy%.')
    dynamic_form.add_field('handy','Handy', TextField)
    dynamic_form.add_validator('handy', EqualTo, '%mobile%', message='Please fill in the exact same data as %mobile%.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == False
    assert form.errors['mobile_2'] == ['Please fill in the exact same data as handy_2.']
    assert form.errors['handy_2'] == ['Please fill in the exact same data as mobile_2.']
    assert form.mobile_1() == '<input id="mobile_1" name="mobile_1" type="text" value="123456">'
    assert form.handy_1() == '<input id="handy_1" name="handy_1" type="text" value="123456">'
    assert form.mobile_2() == '<input id="mobile_2" name="mobile_2" type="text" value="456789">'
    assert form.handy_2() == '<input id="handy_2" name="handy_2" type="text" value="987654">'

def test_validator_length_error(setup):
    """ Test Length validator
    No set - Error situation.
    Field middle_name is too short.
    """
    post = deepcopy(setup)
    post.add(u'middle_name', 'foo')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('middle_name','Middle Name', TextField)
    dynamic_form.add_validator('middle_name', Length, min=4, max=10, message='Please enter length between 4 and 10 characters.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == False
    assert form.errors['middle_name'] == ['Please enter length between 4 and 10 characters.']
    assert form.middle_name() == '<input id="middle_name" name="middle_name" type="text" value="foo">'

def test_validator_length_correct(setup):
    """ Test Length validator
    No set - No error situation.
    Field middle_name is of correct length.
    """
    post = deepcopy(setup)
    post.add(u'middle_name', 'foobar')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('middle_name','Middle Name', TextField)
    dynamic_form.add_validator('middle_name', Length, min=4, max=10, message='Please enter length between 4 and 10 characters.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == True
    assert form.middle_name() == '<input id="middle_name" name="middle_name" type="text" value="foobar">'

def test_validator_length_error_multiple(setup):
    """ Test Length validator
    Multiple sets - Error situation.
    Note that only middle_name_1 is correct.
    """
    post = deepcopy(setup)
    post.add(u'middle_name_1', 'foobar')
    post.add(u'middle_name_2', 'foo')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('middle_name','Middle Name', TextField)
    dynamic_form.add_validator('middle_name', Length, min=4, max=10, message='Please enter length between 4 and 10 characters.')
    form = dynamic_form.process(SimpleForm,
                                post)
   
    form.validate()
    assert form.validate() == False
    assert form.errors['middle_name_2'] == ['Please enter length between 4 and 10 characters.']
    assert form.middle_name_1() == '<input id="middle_name_1" name="middle_name_1" type="text" value="foobar">'
    assert form.middle_name_2() == '<input id="middle_name_2" name="middle_name_2" type="text" value="foo">'

def test_validator_numberrange_error(setup):
    """ Test NumberRange validator
    No set - Error situation.
    Field age is outside the range.
    """
    post = deepcopy(setup)
    post.add(u'age', '20')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('age','Age', IntegerField)
    dynamic_form.add_validator('age', NumberRange, min=30, max=40, message='Please enter an age between %(min)s to %(max)s.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == False
    assert form.errors['age'] == ['Please enter an age between 30 to 40.']
    assert form.age() == '<input id="age" name="age" type="text" value="20">'

def test_validator_numberrange_success(setup):
    """ Test NumberRange validator
    No set - No error situation.
    Field age is within range.
    """
    post = deepcopy(setup)
    post.add(u'age', '32')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('age','Age', IntegerField)
    dynamic_form.add_validator('age', NumberRange, min=30, max=40, message='Please enter an age between %(min)s to %(max)s.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == True
    assert form.age() == '<input id="age" name="age" type="text" value="32">'

def test_validator_numberrange_error_multiple(setup):
    """ Test NumberRange validator
    Sets - Error situation.
    Note, only age_3 is within range.
    """
    post = deepcopy(setup)
    post.add(u'age_1', '4')
    post.add(u'age_2', '12')
    post.add(u'age_3', '30')
    post.add(u'age_4', '42')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('age','Age', IntegerField)
    dynamic_form.add_validator('age', NumberRange, min=30, max=40, message='Please enter an age between %(min)s to %(max)s.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == False
    assert form.errors['age_1'] == ['Please enter an age between 30 to 40.']
    assert form.errors['age_2'] == ['Please enter an age between 30 to 40.']
    assert form.errors['age_4'] == ['Please enter an age between 30 to 40.']
    assert form.age_1() == '<input id="age_1" name="age_1" type="text" value="4">'
    assert form.age_2() == '<input id="age_2" name="age_2" type="text" value="12">'
    assert form.age_3() == '<input id="age_3" name="age_3" type="text" value="30">'
    assert form.age_4() == '<input id="age_4" name="age_4" type="text" value="42">'

def test_validator_anyof_error(setup):
    """ Test NumberRange validator
    No set - Error situation.
    Field hobby has an invalid selection.
    """
    post = deepcopy(setup)
    post.add(u'hobby', 'photography')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('hobby','Hobby', TextField)
    dynamic_form.add_validator('hobby', AnyOf, ['cylcing','swimming','hacking'], message='Please enter only allowed hobbies.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == False
    assert form.errors['hobby'] == ['Please enter only allowed hobbies.']
    assert form.hobby() == '<input id="hobby" name="hobby" type="text" value="photography">'

def test_validator_anyof_success(setup):
    """ Test NumberRange validator
    No set - No error situation.
    Field hobby has a valid selection.
    """
    post = deepcopy(setup)
    post.add(u'hobby', 'swimming')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('hobby','Hobby', TextField)
    dynamic_form.add_validator('hobby', AnyOf, ['cylcing','swimming','hacking'], message='Please enter only allowed hobbies.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == True
    assert form.hobby() == '<input id="hobby" name="hobby" type="text" value="swimming">'

def test_validator_anyof_error_multiple(setup):
    """ Test AnyOf validator
    Sets - Error situation.
    Note, only hobby_3 has a valid hobby.
    """
    post = deepcopy(setup)
    post.add(u'hobby_1', 'sleeping')
    post.add(u'hobby_2', 'eating')
    post.add(u'hobby_3', 'swimming')
    post.add(u'hobby_4', 'gaming')

    dynamic_form = WTFormsDynamicFields()
    dynamic_form.add_field('hobby','Hobby', TextField)
    dynamic_form.add_validator('hobby', AnyOf, ['cylcing','swimming','hacking'], message='Please enter only allowed hobbies.')
    form = dynamic_form.process(SimpleForm,
                                post)
    
    form.validate()
    assert form.validate() == False
    assert form.errors['hobby_1'] == ['Please enter only allowed hobbies.']
    assert form.errors['hobby_2'] == ['Please enter only allowed hobbies.']
    assert form.errors['hobby_4'] == ['Please enter only allowed hobbies.']
    assert form.hobby_1() == '<input id="hobby_1" name="hobby_1" type="text" value="sleeping">'
    assert form.hobby_2() == '<input id="hobby_2" name="hobby_2" type="text" value="eating">'
    assert form.hobby_3() == '<input id="hobby_3" name="hobby_3" type="text" value="swimming">'
    assert form.hobby_4() == '<input id="hobby_4" name="hobby_4" type="text" value="gaming">'

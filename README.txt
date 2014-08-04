WTForms Dynamic Fields
======================

Simple wrapper to add "dynamic" (sets of) fields to an already
instantiated WTForms form.

Installation
------------

Simply use pip to install:

.. code:: bash

    pip install wtforms-dynamic-fields

A few notes before using this module
------------------------------------

If you simply want to add one field to an already existing form, it may
be less overhead to simply use *setattr*:

.. code:: python

    setattr(Form, field_name, TextField(field_label, validators=[InputRequired()]))

Doing so will attach a text field, with one validator to the "Form"
object. This module is intended for slightly more complex scenarios and
to offer an easier way of configuration.

Also, this module, in its current state, is developed to scratch a
personal itch - simple server side validation of dynamic fields (through
WTForms itself). It is most likely missing some needed flexibility
and/or features, so do not hesitate to pinch in or drop me a line!

Quick overview
--------------

Adding a field
~~~~~~~~~~~~~~

The method *add\_field()* is used to add a field to the modules
configuration.

Usage: add\_field('machine name', 'label name', WTFormField, \*args,
\*\*kwargs)

Adding a validator
~~~~~~~~~~~~~~~~~~

The method *add\_validator()* is used to add a validator to an added
field configuration.

Usage: add\_validator('field\_machine\_name', WTFormValidator, \*args,
\*\*kwargs)

-  Decorate field machine name arguments with %'s
   (%some\_field\_machine\_name) to have them automatically suffixed
   with a set number if applicable. More on this below.

Apply the configuration to a form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have setup your configuration using the above methods, you can
apply it to any valid WTForm instance.

Usage: process(ValidFormClass(), POST)

Note that *POST* has to be a MultiDict, which is already the case with
most frameworks like Flask, Django, ...

Basic usage
-----------

The idea behind this module is that you can add "dynamic" fields to a
form that has already been created. "Dynamic" here means fields that are
not rendered (nor present in the original form object) initially, but
get injected into the DOM afterwards.

The module uses the POST variables together with a user defined
configuration to determine which fields are new and are allowed to be
processed.

The first thing you need, obviously, is a valid WTForms instance to put
the new fields on. Say, for example, we have a form that contains a
first name and a last name field, this would be declared as follows:

.. code:: python

    from wtforms import Form, TextField
    from wtforms.validators import InputRequired

    class PersonalFile(Form):
        """ A personal file form. """
        first_name = TextField('First name, validators=[InputRequired()])
        last_name = TextField('Last name, validators=[InputRequired()])

When we present this form to our user, we wish to have the ability to
optionally add an email address and make it required once added.

In most cases, to make for a nice user experience, we go ahead an create
a button that has some JavaScript bound to it which will inject the new
email input field. Also, because we all like instant feedback glory, we
could add some client side validation in our JavaScript to catch
mistakes early and prevent a round trip to the server.

However, we also want this new email address field to be correctly
validated *on the server* and, in case when validation fails, be
rendered back to the user for inspection. We do not want to write our
own validation code for this field, but leverage the power of the
already present, full-blown WTForms form library to do the heavy
lifting.

This is where this module steps in.

First you will need an instance of the module:

.. code:: python

    dynamic = WTFormDynamicFields()

Next you will need to build the configuration which will hold the
allowed, dynamic fields (and their validators). To do this, you use the
"add\_field" method: define the fields machine name, the label and
finally a WTForms field type:

.. code:: python

    dynamic.add_field('email', 'Email address', TextField)

Optionally, you can pass \*args and \*\*kwargs to the field as well.

Of course, the machine name of the field needs to correspond with the
input's "name" attribute as injected by JavaScript. Also notice we do
not add any parenthesis after the WTForms field type (TextField).

If needed, you can also apply optional validators by using the
"add\_validator" method. You define on which field you wish to apply the
validator and you pass in a WTForms validator:

.. code:: python

    dynamic.add_validator('email', InputRequired, args={'message':'This field is required'})

Here too you have the ability to pass in optional *args and *\ kwargs to
the validator. Again, no parenthesis after InputRequired, its arguments
will be bound by the module later on.

Now that you have added this email field and pushed a validator on it,
you are ready to process your form. For the form to be processed, you
will need your original form (*PersonalFile* in our case) and the POST
that comes back from the server.

Normally, you would bind your form variable directly to the WTForm
instance:

.. code:: python

    form = PersonalFile()

To enable this module to process you form, however, you simply need to
wrap its "process" method around it and add the incoming POST:

.. code:: python

    form = dynamic.process(PersonalFile, request.post)

\*Note: the POST is expected to be a MultiDict data type (which is the
case with most frameworks like Flask, Django, ...).

Now the form will pick up the optional email field when injected and
make the validation fail server side if the field is left empty.
Removing the field from the DOM will make your form pass validation
again (given that you filled in the first\_name and last\_name fields,
that is).

Usage with sets
===============

Now imagine the use case where you which to capture not one, but an
undefined amount of email address in that same form and have them all
validated correctly.

With WTForms Dynamic Fields, this is trivial as the module supports sets
- multiple fields of the same kind. To support these sets in your forms,
you only need to uphold a simple naming convention: "\_X" where X is a
number.

If we would add, say, four email fields, these HTML inputs would look
like this:

.. code:: html

    <input type="text" name="email_1" />
    <input type="text" name="email_2" />
    <input type="text" name="email_3" />
    <input type="text" name="email_4" />

The fun fact is, you would not have to change anything to the code we
used in the previous example. The module will derive the canonical name
of each field ("email" in this case) and apply the user defined
configuration for the email field to each individually.

Advanced usage with sets
========================

A more complex scenario could occur when you would have a set comprised
out of two or more fields that are dependent on one another.

For example, to elaborate on our email scenario from above, imagine we
wish to also capture a telephone number with each email. But, to up the
stakes, we only allow one of the two fields to be filled in.

This would require a dependency between the two fields - a validator
which checks if its field is filled in and the other one is not. Such a
validator would take the *other* field's name as an argument:

::

    RequiredIfEmpty('email')

The above validator would be put on the "telephone" field to check if
the email field was left empty.

Now if you have multiple sets of these fields, each field name will be
suffixed with a number, like we have seen before:

.. code:: html

    <div><input type="text" name="email_1" /><input type="text" name="telephone_1" /></div>
    <div><input type="text" name="email_2" /><input type="text" name="telephone_2" /></div>
    <div><input type="text" name="email_3" /><input type="text" name="telephone_3" /></div>
    <div><input type="text" name="email_4" /><input type="text" name="telephone_4" /></div>

So which field machine name would you have to pass to the validator in
such a use case?

For this, the WTForms Dynamic Fields module provides the ability to wrap
a field name argument with % signs.

.. code:: python

    dynamic.add_field('telephone, 'Telephone number, TextField)
    dynamic.add_validator('telephone, RequiredIfEmpty, '%email%')

The module detects when it is processing a set of fields (derived from
the "*X" naming convention) and as such, when wrapping your field name
with % signs, will append the correct suffix to the field when binding
the arguments to the validator. So if we would be looking at email*\ 4,
once expanded, the above code will translate to:

.. code:: python

    telephone_4 = TextField('Telephone number', validators=[RequiredIfEmpty('email_4')])

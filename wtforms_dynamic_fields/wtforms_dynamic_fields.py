import re
import sys
from wtforms.form import FormMeta

class WTFormsDynamicFields():
    """ Add dynamic (set) fields to a WTForm.
    
    Instantiating this class will merely create a configuration
    dictionary on which you can add fields and validators using
    the designated methods "add_field" and "add_validator".

    Calling the "process" method will take care of
    actually applying the build configuration to the WTForm form.

    This method will take a WTForm form object and attach new
    fields to it according to a match between what is in the POST
    and what is defined in the build configuration dictionary.
    
    It has the added ability to process sets of fields that
    are suffixed with the convention of '_X' where X is a number.

    For ease of configuration, these set names will be traced back
    to their canonical name so that each of these fields only have
    to be defined once in the configuration.

    Inside the configuration there is the ability to reference
    other fields within the validator arguments with the convention
    of surrounding it with % signs. Fields that belong to a set 
    will be automatically suffixed with their set number (_X)
    when they are bound to the validator.

    The latter brings the power to reference set fields with their
    canonical name without needing to care about the set number that
    will be used later on when injecting them in the DOM.
    """

    def __init__(self, flask_wtf=False):
        """ Class init.
        :param flask_wtf: Is this form a Flask WTF or a plain WTF instance?
        """
        self._dyn_fields = {}
        self.flask_wtf=flask_wtf

    def add_field(self, name, label, field_type, *args, **kwargs):
        """ Add the field to the internal configuration dictionary. """
        if name in self._dyn_fields:
            raise AttributeError('Field already added to the form.')
        else:
            self._dyn_fields[name] = {'label': label, 'type': field_type,
                                      'args': args, 'kwargs': kwargs}

    def add_validator(self, name, validator, *args, **kwargs):
        """ Add the validator to the internal configuration dictionary.

        :param name:
            The field machine name to apply the validator on
        :param validator:
            The WTForms validator object
        The rest are optional arguments and keyword arguments that
        belong to the validator. We let them simply pass through
        to be checked and bound later.
        """
        if name in self._dyn_fields:
            if 'validators' in self._dyn_fields[name]:
                self._dyn_fields[name]['validators'].append(validator)
                self._dyn_fields[name][validator.__name__] = {}
                if args:
                    self._dyn_fields[name][validator.__name__]['args'] = args
                if kwargs:
                    self._dyn_fields[name][validator.__name__]['kwargs'] = kwargs
            else:
                self._dyn_fields[name]['validators'] = []
                self.add_validator(name, validator, *args, **kwargs)
        else:
            raise AttributeError('Field "{0}" does not exist. '
                                 'Did you forget to add it?'.format(name))

    @staticmethod
    def iteritems(dict):
        """ Refusing to use a possible memory hugging
        Python2 .items() method. So for providing
        both Python2 and 3 support, setting up iteritems()
        as either items() in 3 or iteritems() in 2.
        """
        if sys.version_info[0] >= 3:
            return dict.items()
        else:
            return dict.iteritems()

    def process(self, form, post):
        """ Process the given WTForm Form object.

        Itterate over the POST values and check each field
        against the configuration that was made.

        For each field that is valid, check all the validator
        parameters for possible %field% replacement, then bind
        these parameters to their validator.

        Finally, add the field together with their validators
        to the form.

        :param form:
            A valid WTForm Form object
        :param post:
            A MultiDict with the POST variables
        """

        if not isinstance(form, FormMeta):
            raise TypeError('Given form is not a valid WTForm.')

        re_field_name = re.compile(r'\%([a-zA-Z0-9_]*)\%')

        class F(form):
            pass

        for field, data in post.iteritems():
            if field in F():
                # Skip it if the POST field is one of the standard form fields.
                continue
            else:
                if field in self._dyn_fields:
                    # If we can find the field name directly, it means the field
                    # is not a set so just set the canonical name and go on.
                    field_cname = field
                    # Since we are not in a set, (re)set the current set.
                    current_set_number = None
                elif (field.split('_')[-1].isdigit()
                      and field[:-(len(field.split('_')[-1]))-1] in self._dyn_fields.keys()):
                    # If the field can be split on underscore characters,
                    # the last part contains only digits and the 
                    # everything *but* the last part is found in the
                    # field configuration, we are good to go.
                    # (Cowardly refusing to use regex here).
                    field_cname = field[:-(len(field.split('_')[-1]))-1]
                    # Since we apparently are in a set, remember the
                    # the set number we are at.
                    current_set_number = str(field.split('_')[-1])
                else:
                    # The field did not match to a canonical name
                    # from the fields dictionary or the name
                    # was malformed, throw it out.
                    continue

            # Since the field seems to be a valid one, let us
            # prepare the validator arguments and, if we are in a set
            # replace the %field_name% convention where we find it.
            validators = []
            if 'validators' in self._dyn_fields[field_cname]:
                for validator in self._dyn_fields[field_cname]['validators']:
                    args = []
                    kwargs = {}
                    if 'args' in self._dyn_fields[field_cname]\
                       [validator.__name__]:
                        if not current_set_number:
                            args = self._dyn_fields[field_cname]\
                                   [validator.__name__]['args']
                        else:
                            # If we are currently in a set, append the set number
                            # to all the words that are decorated with %'s within
                            # the arguments.
                            for arg in self._dyn_fields[field_cname]\
                                [validator.__name__]['args']:
                                try:
                                    arg = re_field_name.sub(r'\1'+'_'+current_set_number,
                                                            arg)
                                except:
                                    # The argument does not seem to be regex-able
                                    # Probably not a string, thus we can skip it.
                                    pass
                                args.append(arg)
                    if 'kwargs' in self._dyn_fields[field_cname]\
                       [validator.__name__]:
                        if not current_set_number:
                            kwargs = self._dyn_fields[field_cname]\
                                     [validator.__name__]['kwargs']
                        else:
                            # If we are currently in a set, append the set number
                            # to all the words that are decorated with %'s within
                            # the arguments.
                            for key, arg in self.iteritems(self._dyn_fields[field_cname]\
                                [validator.__name__]['kwargs']):
                                try:
                                    arg = re_field_name.sub(r'\1'+'_'+current_set_number,
                                                            arg)
                                except:
                                    # The argument does not seem to be regex-able
                                    # Probably not a string, thus we can skip it.
                                    pass
                                kwargs[key] = arg
                    # Finally, bind arguments to the validator
                    # and add it to the list
                    validators.append(validator(*args, **kwargs))

            # The field is setup, it is time to add it to the form.
            field_type = self._dyn_fields[field_cname]['type']
            field_label = self._dyn_fields[field_cname]['label']
            field_args = self._dyn_fields[field_cname]['args']
            field_kwargs = self._dyn_fields[field_cname]['kwargs']

            setattr(F, field, field_type(field_label,
                                         validators=validators,
                                         *field_args,
                                         **field_kwargs))

        # Create an instance of the form with the newly
        # created fields and give it back to the caller.
        if self.flask_wtf:
            # Flask WTF overrides the form initialization
            # and already injects the POST variables.
            form = F()
        else:
            form = F(post)
        return form

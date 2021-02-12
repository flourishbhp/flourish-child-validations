import re
from django.core.exceptions import ValidationError
from edc_base.utils import relativedelta
from edc_constants.constants import NO
from edc_form_validators import FormValidator


class ChildAssentFormValidator(FormValidator):

    def clean(self):

        cleaned_data = self.cleaned_data

        self.required_if(
            NO,
            field='is_literate',
            field_required='witness_name')

        self.clean_full_name_syntax()
        self.clean_initials_with_full_name()
        self.validate_identity_number(cleaned_data)
        self.validate_dob(cleaned_data)

    def clean_full_name_syntax(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if not re.match(r'^[A-Z]+$|^([A-Z]+[ ][A-Z]+)$', first_name):
            message = {'first_name': 'Ensure first name is letters (A-Z) in '
                       'upper case, no special characters, except spaces.'}
            self._errors.update(message)
            raise ValidationError(message)

        if not re.match(r'^[A-Z-]+$', last_name):
            message = {'last_name': 'Ensure last name is letters (A-Z) in '
                       'upper case, no special characters, except hyphens.'}
            self._errors.update(message)
            raise ValidationError(message)

        if first_name and last_name:
            if first_name != first_name.upper():
                message = {'first_name': 'First name must be in CAPS.'}
                self._errors.update(message)
                raise ValidationError(message)
            elif last_name != last_name.upper():
                message = {'last_name': 'Last name must be in CAPS.'}
                self._errors.update(message)
                raise ValidationError(message)

    def clean_initials_with_full_name(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        initials = cleaned_data.get("initials")
        try:
            middle_name = None
            is_first_name = False
            new_first_name = None
            if len(first_name.split(' ')) > 1:
                new_first_name = first_name.split(' ')[0]
                middle_name = first_name.split(' ')[1]

            if (middle_name and
                (initials[:1] != new_first_name[:1] or
                 initials[1:2] != middle_name[:1])):
                is_first_name = True

            elif not middle_name and initials[:1] != first_name[:1]:
                is_first_name = True

            if is_first_name or initials[-1:] != last_name[:1]:
                raise ValidationError(
                    {'initials': 'Initials do not match full name.'},
                    params={
                        'initials': initials,
                        'first_name': first_name,
                        'last_name': last_name},
                    code='invalid')
        except (IndexError, TypeError):
            raise ValidationError('Initials do not match fullname.')

    def validate_identity_number(self, cleaned_data=None):
        if cleaned_data.get('identity') != cleaned_data.get('confirm_identity'):
            msg = {'identity':
                   '\'Identity\' must match \'confirm identity\'.'}
            self._errors.update(msg)
            raise ValidationError(msg)
        if cleaned_data.get('identity_type') == 'country_id':
            if len(cleaned_data.get('identity')) != 9:
                msg = {'identity':
                       'Country identity provided should contain 9 values. '
                       'Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            if cleaned_data.get('identity')[4] != '2':
                msg = {'identity':
                       'Identity provided indicates participant is Male. Please '
                       'correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_dob(self, cleaned_data=None):
        consent_datetime = cleaned_data.get('consent_datetime')
        consent_age = relativedelta(
            consent_datetime.date(), cleaned_data.get('dob')).years
        age_in_years = None

        try:
            consent_obj = self.subject_consent_cls.objects.get(
                screening_identifier=self.cleaned_data.get('screening_identifier'),)
        except self.subject_consent_cls.DoesNotExist:
            if consent_age < 7:
                msg = {'dob':
                       'Participant is younger than 7 years of age. Assent is not needed.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        else:
            age_in_years = relativedelta(
                consent_datetime.date(), consent_obj.dob).years
            if consent_age != age_in_years:
                message = {'dob':
                           'In previous consent the derived age of the '
                           f'participant is {age_in_years}, but age derived '
                           f'from the DOB is {consent_age}.'}
                self._errors.update(message)
                raise ValidationError(message)

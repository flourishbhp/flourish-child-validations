import re
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import relativedelta
from edc_constants.constants import NO, FEMALE, MALE
from edc_form_validators import FormValidator


class ChildAssentFormValidator(FormValidator):

    prior_screening_model = 'flourish_caregiver.screeningpriorbhpparticipants'

    child_dataset_model = 'flourish_child.childdataset'

    child_assent_model = 'flourish_child.childassent'

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    @property
    def bhp_prior_screening_cls(self):
        return django_apps.get_model(self.prior_screening_model)

    @property
    def child_dataset_cls(self):
        return django_apps.get_model(self.child_dataset_model)

    @property
    def assent_cls(self):
        return django_apps.get_model(self.child_assent_model)

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    def clean(self):

        cleaned_data = self.cleaned_data

        self.required_if(
            NO,
            field='is_literate',
            field_required='witness_name')

        self.validate_against_child_consent()
        self.clean_full_name_syntax()
        self.clean_initials_with_full_name()
        self.validate_gender()
        self.validate_identity_number(cleaned_data)
        self.validate_preg_testing()
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
        identity = cleaned_data.get('identity')
        confirm_identity = cleaned_data.get('confirm_identity')
        identity_type = cleaned_data.get('identity_type')
        if not re.match('[0-9]+$', identity):
            message = {'identity': 'Identity number must be digits.'}
            self._errors.update(message)
            raise ValidationError(message)
        if identity != confirm_identity:
            msg = {'identity':
                   '\'Identity\' must match \'confirm identity\'.'}
            self._errors.update(msg)
            raise ValidationError(msg)
        if identity_type in ['country_id', 'birth_cert']:
            if len(identity) != 9:
                msg = {'identity':
                       f'{identity_type} provided should contain 9 values. '
                       'Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            gender = cleaned_data.get('gender')
            if gender == FEMALE and identity[4] != '2':
                msg = {'identity':
                       'Participant is Female. Please correct the identity number.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            if gender == MALE and identity[4] != '1':
                msg = {'identity':
                       'Participant is Male. Please correct the identity number.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_dob(self, cleaned_data=None):

        if self.caregiver_child_consent.child_dob != cleaned_data.get('dob'):
            msg = {'dob':
                   'Child dob must match dob specified for the caregiver consent'
                   f' on behalf of child {self.caregiver_child_consent.child_dob}.'}
            self._errors.update(msg)
            raise ValidationError(msg)

        assent_datetime = cleaned_data.get('consent_datetime')
        assent_age = relativedelta(
            assent_datetime.date(), cleaned_data.get('dob')).years
        age_in_years = None

        try:
            assent_obj = self.assent_cls.objects.get(
                subject_identifier=self.cleaned_data.get('subject_identifier'),)
        except self.assent_cls.DoesNotExist:
            if assent_age < 7 or assent_age >= 18:
                msg = {'dob':
                       f'Participant is {assent_age} years of age. Child assent'
                       ' is not required.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        else:
            age_in_years = relativedelta(
                assent_datetime.date(), assent_obj.dob).years
            if assent_age != age_in_years:
                message = {'dob':
                           'In previous consent the derived age of the '
                           f'participant is {age_in_years}, but age derived '
                           f'from the DOB is {assent_age}.'}
                self._errors.update(message)
                raise ValidationError(message)

    def validate_gender(self):
        if self.caregiver_child_consent:
            infant_sex = self.caregiver_child_consent.gender
            gender = self.cleaned_data.get('gender')
            if gender != infant_sex:
                msg = {'gender':
                       f'Child\'s gender is {self.caregiver_child_consent.infant_sex} from '
                       'the caregiver consent on behalf of child. Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_preg_testing(self):
        self.applicable_if(
            FEMALE,
            field='gender',
            field_applicable='preg_testing')

    def validate_against_child_consent(self):
        cleaned_data = self.cleaned_data
        fields = [key for key in cleaned_data.keys() if key != 'consent_datetime']
        for field in fields:
            child_consent_value = getattr(self.caregiver_child_consent, field, None)
            field_value = cleaned_data.get(field)
            if child_consent_value and child_consent_value != field_value:
                message = {field:
                           f'{field_value} does not match {child_consent_value} '
                           'from the caregiver consent on behalf of child. Please '
                           'correct this.'}
                self._errors.update(message)
                raise ValidationError(message)

    @property
    def caregiver_child_consent(self):

        try:
            child_consent = self.caregiver_child_consent_cls.objects.get(
                subject_identifier=self.cleaned_data.get('subject_identifier'))
        except self.caregiver_child_consent_cls.DoesNotExist:
            raise ValidationError('Caregiver child consent matching query does not exist.')
        else:
            return child_consent

    @property
    def prior_screening(self):
        try:
            bhp_prior = self.bhp_prior_screening_cls.objects.get(
                screening_identifier=self.cleaned_data.get('screening_identifier'))
        except self.bhp_prior_screening_cls.DoesNotExist:
            return None
        else:
            return bhp_prior

    @property
    def child_dataset(self):
        if self.prior_screening:
            try:
                child_dataset = self.child_dataset_cls.objects.get(
                    study_maternal_identifier=self.prior_screening.study_maternal_identifier)
            except self.child_dataset_cls.DoesNotExist:
                return None
            else:
                return child_dataset
        return None

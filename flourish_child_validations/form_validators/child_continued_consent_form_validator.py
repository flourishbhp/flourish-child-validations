import re
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import relativedelta
from edc_constants.constants import NO, FEMALE, MALE
from edc_form_validators import FormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class ChildContinuedConsentFormValidator(ChildFormValidatorMixin, FormValidator):

    prior_screening_model = 'flourish_caregiver.screeningpriorbhpparticipants'

    child_dataset_model = 'flourish_child.childdataset'

    childcontinued_consent_model = 'flourish_child.childcontinuedconsent'

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    @property
    def bhp_prior_screening_cls(self):
        return django_apps.get_model(self.prior_screening_model)

    @property
    def child_dataset_cls(self):
        return django_apps.get_model(self.child_dataset_model)

    @property
    def childcontinued_consent_cls(self):
        return django_apps.get_model(self.childcontinued_consent_model)

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    def clean(self):

        cleaned_data = self.cleaned_data

        self.validate_consent_version_obj(
            self.cleaned_data.get('subject_identifier'))

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
        super().clean()

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

        consent_datetime = cleaned_data.get('consent_datetime')
        consent_age = relativedelta(
            consent_datetime.date(), cleaned_data.get('dob')).years if consent_datetime else None
        age_in_years = None

        try:
            consent_obj = self.childcontinued_consent_cls.objects.filter(
                subject_identifier=self.cleaned_data.get('subject_identifier')).latest('version')
        except self.childcontinued_consent_cls.DoesNotExist:
            if consent_age and consent_age < 18:
                msg = {'dob':
                       f'Participant is {consent_age} years of age. Child '
                       'continued consent is not required.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        else:
            age_in_years = relativedelta(
                consent_datetime.date(), consent_obj.dob).years if consent_datetime else None
            if age_in_years and consent_age != age_in_years:
                message = {'dob':
                           'In previous consent the derived age of the '
                           f'participant is {age_in_years}, but age derived '
                           f'from the DOB is {consent_age}.'}
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
        identity = cleaned_data.get('identity')
        fields = [key for key in cleaned_data.keys() if key not in 
                  ['consent_datetime','identity_type','identity']]
        for field in fields:
            child_consent_value = getattr(
                self.caregiver_child_consent, field, None)
            field_value = cleaned_data.get(field)
            self.check_identity_fields(
                field, field_value, identity, child_consent_value)
            if self._errors:
                raise ValidationError(self._errors)

    def check_identity_fields(self, field, field_value, identity, child_consent_value):
        """
        Validate the identity and child consent values, adding appropriate errors when mismatched.
        """
        if field == 'identity_type':
            child_identity = getattr(
                self.caregiver_child_consent, 'identity', None)

            # Common error for mismatched identities
            def add_identity_error(reason):
                self.capture_error_message(
                    f'The identity value "{identity}" does not match the child consent identity value "{child_identity}". {reason}'
                )

            # Check identity mismatch based on field value and child consent value
            if child_consent_value == field_value and child_identity != identity:
                add_identity_error("")
                return

            if field_value == 'country_id' and child_consent_value == 'birth_cert' and child_identity != identity:
                add_identity_error(
                    'This is required when the identity type is "country_id" '
                    'and the child consent identity type is "birth_cert".'
                )
                return
        # Add error if child consent value mismatches the field value
        if child_consent_value and child_consent_value != field_value:
            self.capture_error_message(
                f'{field_value} does not match {child_consent_value} from the caregiver consent on behalf of the child. '
                'Please correct this.'
            )

    @property
    def caregiver_child_consent(self):
        try:
            child_consent = self.caregiver_child_consent_cls.objects.filter(
                subject_identifier=self.cleaned_data.get('subject_identifier')).latest('version')
        except self.caregiver_child_consent_cls.DoesNotExist:
            raise ValidationError(
                'Caregiver child consent matching query does not exist.')
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

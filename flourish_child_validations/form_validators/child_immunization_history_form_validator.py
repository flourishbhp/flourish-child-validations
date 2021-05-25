from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import age, get_utcnow
from edc_form_validators import FormValidator
from edc_constants.constants import YES


class VaccinesReceivedFormValidator(FormValidator):

    caregiver_child_consent = 'flourish_caregiver.caregiverchildconsent'

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent)

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_immunization_history').subject_identifier
        cleaned_data = self.cleaned_data
        self.validate_hpv_vaccine(cleaned_data)
        self.validate_vaccine_received(cleaned_data)
        self.validate_received_vaccine_fields(cleaned_data)
        self.validate_vaccination_at_birth(cleaned_data)
        self.validate_hepatitis_vaccine(cleaned_data)
        self.validate_dpt_vaccine(cleaned_data)
        self.validate_haemophilus_vaccine(cleaned_data)
        self.validate_pcv_vaccine(cleaned_data)
        self.validate_polio_vaccine(cleaned_data)
        self.validate_rotavirus_vaccine(cleaned_data)
        self.validate_measles_vaccine(cleaned_data)
        self.validate_pentavalent_vaccine(cleaned_data)
        self.validate_vitamin_a_vaccine(cleaned_data)
        self.validate_ipv_vaccine(cleaned_data)
        self.validate_diptheria_tetanus_vaccine(cleaned_data)

    @property
    def caregiver_child_consent_model(self):
        try:
            caregiver_child = self.caregiver_child_consent_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except self.caregiver_child_consent_cls.DoesNotExist:
            return None
        else:
            return caregiver_child

    def validate_vaccine_received(self, cleaned_data=None):
        condition = cleaned_data.get(
            'child_immunization_history').vaccines_received == YES
        self.required_if_true(
            condition,
            field_required='received_vaccine_name',
            required_msg=('You mentioned that vaccines were received. Please '
                          'indicate which ones on the table.'))

    def validate_received_vaccine_fields(self, cleaned_data=None):
        fields_required = ('date_given', 'child_age')
        for required in fields_required:
            self.required_if_not_none(
                field='received_vaccine_name',
                field_required=required,
                required_msg=('You provided a vaccine name {}. {} field '
                              'is required. Please correct'.format(
                                  cleaned_data.get('received_vaccine_name'),
                                  required)))

    def validate_hpv_vaccine(self, cleaned_data):
        received_vaccine_name = cleaned_data.get('received_vaccine_name')
        if self.caregiver_child_consent_model:
            child_dob = self.caregiver_child_consent_model.child_dob
            child_age = age(child_dob, get_utcnow().date()).years
            if child_age <= 12 and received_vaccine_name == 'hpv_vaccine':
                message = {'received_vaccine_name':
                           'Child age is less than 12, cannot select HPV vaccine'}
                self._errors.update(message)
                raise ValidationError(message)
        if cleaned_data.get('child_age') == 'adolescent':
            if received_vaccine_name != 'hpv_vaccine':
                msg = {'child_age':
                       'Cannot select Adolescent if vaccine is not HPV.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        if (received_vaccine_name == 'hpv_vaccine' and
                not cleaned_data.get('child_age') == 'adolescent'):
            msg = {'child_age':
                   'HPV vaccine selected, child age should be adolescent.'}
            self._errors.update(msg)
            raise ValidationError(msg)

    def validate_vaccination_at_birth(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'bcg':
            if cleaned_data.get('child_age') not in ['At Birth', 'After Birth']:
                msg = {'child_age':
                       'BCG vaccination is ONLY given at birth or few'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_hepatitis_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'hepatitis_b':
            if cleaned_data.get('child_age') not in ['At Birth', '2', '3', '4']:
                msg = {'child_age':
                       'Hepatitis B can only be administered '
                       'at birth or 2 or 3 or 4 months of infant life'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_dpt_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'dpt':
            if cleaned_data.get('child_age') not in ['2', '3', '4']:
                msg = {'child_age':
                       'DPT. Diphtheria, Pertussis and Tetanus can only '
                       'be administered at 2 or 3 or 4 months ONLY.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_haemophilus_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'haemophilus_influenza':
            if cleaned_data.get('child_age') not in ['2', '3', '4']:
                msg = {'child_age':
                       'Haemophilus Influenza B vaccine can only be given '
                       'at 2 or 3 or 4 months of infant life.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_pcv_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'pcv_vaccine':
            if cleaned_data.get('child_age') not in ['2', '3', '4']:
                msg = {'child_age':
                       'The PCV [Pneumonia Conjugated Vaccine], can ONLY be '
                       'administered at 2 or 3 or 4 months of infant life.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_polio_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == '[olio':
            if cleaned_data.get('child_age') not in ['2', '3', '4', '18']:
                msg = {'child_age':
                       'Polio vaccine can only be administered at '
                       '2 or 3 or 4 or 18 months of infant life'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_rotavirus_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'rotavirus':
            if cleaned_data.get('child_age') not in ['2', '3']:
                msg = {'child_age':
                       'Rotavirus is only administered at 2 or 3 months '
                       'of infant life'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_measles_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'measles':
            if cleaned_data.get('child_age') not in ['9', '18']:
                msg = {'child_age':
                       'Measles vaccine is only administered at 9 or 18 '
                       'months of infant life.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_pentavalent_vaccine(self, cleaned_data=None):
        if (cleaned_data.get('received_vaccine_name') == 'pentavalent' and
                cleaned_data.get('child_age') not in ['2', '3', '4']):
            msg = {'child_age':
                   'The Pentavalent vaccine can only be administered '
                   'at 2 or 3 or 4 months of infant life.'}
            self._errors.update(msg)
            raise ValidationError(msg)

    def validate_vitamin_a_vaccine(self, cleaned_data=None):
        if (cleaned_data.get('received_vaccine_name') == 'vitamin_a' and
                cleaned_data.get('child_age') not in ['6-11', '9', '9-12',
                                                      '12-17', '18', '18-29',
                                                      '24-29', '30-35',
                                                      '36-41', '42-47']):
            msg = {'child_age':
                   'Vitamin A is given to children between 6-41 months '
                   'of life'}
            self._errors.update(msg)
            raise ValidationError(msg)

    def validate_ipv_vaccine(self, cleaned_data=None):
        if (cleaned_data.get('received_vaccine_name') == 'inactivated_polio_vaccine' and
                cleaned_data.get('child_age') not in ['4', '9-12']):
            msg = {'child_age':
                   'IPV vaccine is only given at 4 Months. '
                   'of life or 9-12 months'}
            self._errors.update(msg)
            raise ValidationError(msg)

    def validate_diptheria_tetanus_vaccine(self, cleaned_data=None):
        if cleaned_data.get('received_vaccine_name') == 'diphtheria_tetanus':
            if cleaned_data.get('child_age') not in ['18']:
                msg = {'child_age':
                       'Measles vaccine is only administered at 18 '
                       'months of infant life.'}
                self._errors.update(msg)
                raise ValidationError(msg)

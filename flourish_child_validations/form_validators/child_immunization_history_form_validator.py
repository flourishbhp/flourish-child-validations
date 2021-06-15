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
        self.validate_vaccine_received(cleaned_data)
        self.validate_received_vaccine_fields(cleaned_data)
        self.validate_hpv_vaccine(cleaned_data)
        self.validate_dates(cleaned_data)

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
        received_vaccine_name = cleaned_data.get('received_vaccine_name')
        first_dose_dt = cleaned_data.get('first_dose_dt')
        second_dose_dt = cleaned_data.get('second_dose_dt')
        third_dose_dt = cleaned_data.get('third_dose_dt')
        if received_vaccine_name:
            if not (first_dose_dt or second_dose_dt or third_dose_dt):
                message = {'received_vaccine_name':
                           f'You provided a vaccine name {received_vaccine_name}.'
                           'Please provide details on the doses.'}
                self._errors.update(message)
                raise ValidationError(message)
        else:
            if first_dose_dt or second_dose_dt or third_dose_dt:
                message = {'received_vaccine_name':
                           'Please provide the vaccine name before providing '
                           'details on the doses.'}
                self._errors.update(message)
                raise ValidationError(message)

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

    def validate_dates(self, cleaned_data):
        first_dose_dt = cleaned_data.get('first_dose_dt')
        second_dose_dt = cleaned_data.get('second_dose_dt')
        third_dose_dt = cleaned_data.get('third_dose_dt')
        dates = [first_dose_dt, second_dose_dt, third_dose_dt]

        for date in dates:
            dates.remove(date)
            for counter in range(0, len(dates)):
                if dates[counter] == date:
                    message = f'Duplicate entry for date {date}, please correct.'
                    raise ValidationError(message)

        if first_dose_dt > second_dose_dt or first_dose_dt > third_dose_dt:
            message = {'first_dose_dt':
                       'The date of the first dose can not be after the '
                       'second/third dose date.'}
            self._errors.update(message)
            raise ValidationError(message)

        if second_dose_dt > third_dose_dt:
            message = {'second_dose_dt':
                       'The date of the second dose can not be after the '
                       'third dose date.'}
            self._errors.update(message)
            raise ValidationError(message)

    def validate_hpv_vaccine_adolescent(self, cleaned_data, ages={}):
        received_vaccine_name = cleaned_data.get('received_vaccine_name')
        if 'adolescent' in ages.values():
            if received_vaccine_name != 'hpv_vaccine':
                msg = {'received_vaccine_name':
                       'Cannot select age as Adolescent if vaccine is not HPV.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        if received_vaccine_name == 'hpv_vaccine':
            for hpv_field, hpv_age in ages.items():
                if hpv_age and hpv_age != 'adolescent':
                    msg = {hpv_field:
                           'HPV vaccine selected, child age should be adolescent.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_vaccination_at_birth(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'bcg':
            for field, age in ages.items():
                if age and age not in ['At Birth', 'After Birth']:
                    msg = {field:
                           'BCG vaccination is ONLY given at birth or few'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_hepatitis_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'hepatitis_b':
            for field, age in ages.items():
                if age and age not in ['At Birth', '2', '3', '4']:
                    msg = {field:
                           'Hepatitis B can only be administered '
                           'at birth or 2 or 3 or 4 months of infant life'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_dpt_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'dpt':
            for field, age in ages.items():
                if age and age not in ['2', '3', '4']:
                    msg = {field:
                           'DPT. Diphtheria, Pertussis and Tetanus can only '
                           'be administered at 2 or 3 or 4 months ONLY.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_haemophilus_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'haemophilus_influenza':
            for field, age in ages.items():
                if age and age not in ['2', '3', '4']:
                    msg = {field:
                           'Haemophilus Influenza B vaccine can only be given '
                           'at 2 or 3 or 4 months of infant life.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_pcv_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'pcv_vaccine':
            for field, age in ages.items():
                if age and age not in ['2', '3', '4']:
                    msg = {field:
                           'The PCV [Pneumonia Conjugated Vaccine], can ONLY be'
                           ' administered at 2 or 3 or 4 months of infant life.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_polio_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'polio':
            for field, age in ages.items():
                if age and age not in ['2', '3', '4', '18']:
                    msg = {field:
                           'Polio vaccine can only be administered at '
                           '2 or 3 or 4 or 18 months of infant life'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_rotavirus_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'rotavirus':
            for field, age in ages.items():
                if age and age not in ['2', '3']:
                    msg = {field:
                           'Rotavirus is only administered at 2 or 3 months '
                           'of infant life'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_measles_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'measles':
            for field, age in ages.items():
                if age and age not in ['9', '18']:
                    msg = {field:
                           'Measles vaccine is only administered at 9 or 18 '
                           'months of infant life.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_pentavalent_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'pentavalent':
            for field, age in ages.items():
                if age and age not in ['2', '3', '4']:
                    msg = {field:
                           'The Pentavalent vaccine can only be administered '
                           'at 2 or 3 or 4 months of infant life.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_vitamin_a_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'vitamin_a':
            for field, age in ages.items():
                if age and age not in ['6-11', '9', '9-12', '12-17', '18',
                                       '18-29', '24-29', '30-35', '36-41',
                                       '42-47']:
                    msg = {field:
                           'Vitamin A is given to children between 6-41 months'
                           ' of life'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_ipv_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'inactivated_polio_vaccine':
            for field, age in ages.items():
                if age and age not in ['4', '9-12']:
                    msg = {field:
                           'IPV vaccine is only given at 4 Months. '
                           'of life or 9-12 months'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_diptheria_tetanus_vaccine(self, cleaned_data=None, ages={}):
        if cleaned_data.get('received_vaccine_name') == 'diphtheria_tetanus':
            for field, age in ages.items():
                if age and age not in ['18']:
                    msg = {field:
                           'Measles vaccine is only administered at 18 '
                           'months of infant life.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

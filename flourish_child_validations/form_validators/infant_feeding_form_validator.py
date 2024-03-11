from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO, NOT_SURE
from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class InfantFeedingFormValidator(ChildFormValidatorMixin,
                                 CrfOffStudyFormValidator,
                                 FormValidator):

    breast_feeding_model = 'flourish_caregiver.breastfeedingquestionnaire'
    infant_feeding_model = 'flourish_child.infantfeeding'
    infant_birth_model = 'flourish_child.childbirth'

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()
        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))

        self.validate_date_weaned()

        self.breastfeeding_validations()

        self.formula_validations()

        self.other_liquids_validations()

        self.solid_foods_validations()

    def previous_feeding_instance(self):
        infant_feeding_cls = django_apps.get_model(self.infant_feeding_model)

        child_visit = self.cleaned_data.get('child_visit', None)

        while child_visit:
            child_visit = getattr(child_visit, 'previous_visit', False)

            try:
                infant_feeding = infant_feeding_cls.objects.get(
                    child_visit=child_visit)
            except infant_feeding_cls.DoesNotExist:
                continue
            else:
                return infant_feeding

    def breastfeeding_validations(self):

        fields_required = ['bf_start_dt', 'bf_start_dt_est', 'recent_bf_dt',
                           'continuing_to_bf']
        for field in fields_required:
            self.required_if(
                YES,
                field='ever_breastfed',
                field_required=field)

        if self.previous_feeding_instance():
            self.required_if(
                YES,
                field='ever_breastfed',
                field_required='child_weaned')

            self.required_if(
                YES,
                field='child_weaned',
                field_required='dt_weaned')
        else:
            self.required_if(
                NO,
                field='continuing_to_bf',
                field_required='dt_weaned')

        self.required_if(
            YES,
            field='rec_liquids',
            field_required='took_formula')

    def formula_validations(self):

        self.required_if(
            YES,
            field='took_formula',
            field_required='dt_formula_introduced')

        self.not_applicable_if(
            *(NO, NOT_SURE, None),
            field='took_formula',
            field_applicable='formula_first_report')

        self.required_if_not_none(
            field='dt_formula_introduced',
            field_required='dt_formula_est')

        self.required_if(
            YES,
            field='took_formula',
            field_required='formula_feedng_completd')

        fields_required = ['dt_formula_stopd', 'dt_stopd_est']
        for field in fields_required:
            self.required_if(
                YES,
                field='formula_feedng_completd',
                field_required=field)

        self.required_if(
            NO,
            field='formula_feedng_completd',
            field_required='formula_water')

        self.validate_other_specify(field='formula_water')

    def other_liquids_validations(self):

        for field in ['taken_water', 'taken_juice', 'taken_cows_milk',
                      'taken_animal_milk', 'taken_salts']:
            self.required_if(
                YES,
                field='rec_liquids',
                field_required=field)

        self.applicable_if(
            YES,
            field='taken_cows_milk',
            field_applicable='cows_milk_prep')

        for field in ['animal_milk_specify', 'milk_boiled']:
            self.required_if(
                YES,
                field='taken_animal_milk',
                field_required=field)

    def solid_foods_validations(self):

        for field in ['solid_foods_dt', 'solid_foods_age']:
            self.required_if(
                YES,
                field='taken_solid_foods',
                field_required=field)

        self.m2m_required_if(
            YES,
            field='taken_solid_foods',
            m2m_field='solid_foods')

        self.m2m_required_if(
            YES,
            field='provide_response_solid',
            m2m_field='solid_foods_past_week')

        solid_foods = self.cleaned_data.get('solid_foods_past_week')
        selected = [solid.short_name for solid in solid_foods]
        value_field = {'food_grains': 'grain_intake_freq',
                       'food_legume': 'legumes_intake_freq',
                       'food_dairy': 'dairy_intake_freq',
                       'food_flesh': 'flesh_foods_freq',
                       'food_eggs': 'eggs_intake_freq',
                       'food_porridge': 'porridge_intake_freq',
                       'food_vita': 'vitamin_a_fruits_freq',
                       'food_fruitsvege': ['other_fruits_vegies', 'other_fruits_freq'],
                       'food_othersolid': ['other_solids', 'other_solids_freq']}

        for value, field in value_field.items():
            if isinstance(field, list):
                for required in field:
                    self.required_if_true(
                        value in selected,
                        field_required=required)
            else:
                self.required_if_true(
                    value in selected,
                    field_required=field)

    def validate_date_weaned(self):
        dt_weaned = self.cleaned_data.get('dt_weaned', None)
        dt_formula_introduced = self.cleaned_data.get(
            'dt_formula_introduced', None)
        bf_start_dt = self.cleaned_data.get('bf_start_dt', None)

        previous_instance = self.previous_feeding_instance()
        previous_wean_dt = getattr(previous_instance, 'dt_weaned', None)
        if previous_wean_dt and dt_weaned:
            consistent = (dt_weaned == previous_wean_dt)
            if not consistent:
                message = {'dt_weaned':
                           f'The date participant weaned is {previous_wean_dt} '
                           f'from visit {previous_instance.child_visit.visit_code}'
                           ' Date provided is not consistent with this date.'}
                self._errors.update(message)
                raise ValidationError(message)

        self.applicable_if(
            NO,
            field='child_weaned',
            field_applicable='freq_milk_rec')

        prev_formula_dt = getattr(
            previous_instance, 'dt_formula_introduced', None)
        if prev_formula_dt and dt_formula_introduced:
            consistent = (dt_formula_introduced == prev_formula_dt)
            if not consistent:
                message = {'dt_formula_introduced':
                           f'Date infant formula introduced is {prev_formula_dt} '
                           f'from visit {previous_instance.child_visit.visit_code}'
                           ' Date provided is not consistent with this date.'}
                self._errors.update(message)
                raise ValidationError(message)

        self.validate_against_birth_date(
            infant_identifier=self.subject_identifier,
            report_datetime=dt_formula_introduced,
            date_attr='dob',
            message='Date infant formula introduced can not be before child DOB.')

        prev_bf_start_dt = getattr(previous_instance, 'bf_start_dt', None)
        if prev_bf_start_dt and bf_start_dt:
            consistent = (bf_start_dt == prev_bf_start_dt)
            if not consistent:
                message = {'bf_start_dt':
                           f'Date infant started breastfeeding is {prev_bf_start_dt} '
                           f'from visit {previous_instance.child_visit.visit_code}'
                           ' Date provided is not consistent with this date.'}
                self._errors.update(message)
                raise ValidationError(message)

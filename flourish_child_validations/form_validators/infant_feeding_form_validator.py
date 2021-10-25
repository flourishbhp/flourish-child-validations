from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class InfantFeedingFormValidator(ChildFormValidatorMixin,
                                 CrfOffStudyFormValidator,
                                 FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))

        fields_required = ['bf_start_dt', 'bf_start_dt_est', 'recent_bf_dt',
                           'continuing_to_bf']
        for field in fields_required:
            self.required_if(
                YES,
                field='ever_breastfed',
                field_required=field)

        self.required_if(
            NO,
            field='continuing_to_bf',
            field_required='dt_weaned')

        self.applicable_if(
            YES,
            field='ever_breastfed',
            field_applicable='freq_milk_rec')

        self.required_if(
            YES,
            field='rec_liquids',
            field_required='taken_formula')

        fields_required = ['dt_formula_introduced', 'dt_formula_est',
                           'formula_feedng_completd']
        for field in fields_required:
            self.required_if(
                YES,
                field='taken_formula',
                field_required=field)

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

        for field in ['taken_water', 'taken_juice', 'taken_cows_milk',
                      'taken_animal_milk', 'taken_salts']:
            self.required_if(
                YES,
                field='rec_liquids',
                field_required=field)

        self.applicable_if(
            YES,
            field='taken_cows_milk',
            field_applicable='cows_milk_used')

        for field in ['animal_milk_specify', 'milk_boiled']:
            self.required_if(
                YES,
                field='taken_animal_milk',
                field_required=field)

        for field in ['solid_foods_dt', 'solid_foods_age']:
            self.required_if(
                YES,
                field='taken_solid_foods',
                field_required=field)

        self.m2m_required_if(
            YES,
            field='taken_solid_foods',
            m2m_field='solid_foods')

        solid_foods = self.cleaned_data.get('solid_foods')
        selected = [solid.short_name for solid in solid_foods]
        field_value = {'grain_intake_freq': 'grains_roots_tubers',
                       'legumes_intake_freq': 'legumes_nuts',
                       'dairy_intake_freq': 'dairy_products',
                       'flesh_foods_freq': 'flesh_foods',
                       'eggs_intake_freq': 'eggs',
                       'porridge_intake_freq': 'porridge',
                       'vitamin_a_fruits_freq': 'vitamin_a_rich_fruits_vegies'}

        for field, value in field_value.items():
            self.required_if_true(
                value in selected,
                field_required=field)

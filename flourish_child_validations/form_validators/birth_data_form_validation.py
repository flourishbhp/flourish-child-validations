from django import forms
from edc_constants.constants import YES
from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class BirthDataFormValidator(ChildFormValidatorMixin, CrfOffStudyFormValidator,
                             FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))
        self.validate_metrics_avail()
        self.validate_apgar_score()
        self.validate_gestational_age()

    def validate_gestational_age(self):
        """
        Gestional age should be between age of 22 and 43 for the purpose
        of this study
        """
        gestational_age = self.cleaned_data.get('gestational_age', 0)

        if gestational_age:

            if 22 > gestational_age or gestational_age > 43:
                raise forms.ValidationError(
                    {'gestational_age':
                     'Gestational age should be between 22 and 43.'})

        else:
            raise forms.ValidationError({'gestational_age':
                                         'Gestational age is required'})

    def validate_apgar_score(self):
        agpar_list = ['apgar_score_min_1', 'apgar_score_min_5',
                      'apgar_score_min_10']

        for agpar in agpar_list:
            self.required_if(
                YES,
                field='apgar_score',
                field_required=agpar,
                required_msg='If Apgar scored performed, this field is required.')

    def validate_metrics_avail(self):
        fields_dict = {'weight_avail': 'weight_kg',
                       'length_avail': 'infant_length',
                       'head_circ_avail': 'head_circumference', }

        for field, required_field in fields_dict.items():
            self.required_if(
                YES,
                field=field,
                field_required=required_field)

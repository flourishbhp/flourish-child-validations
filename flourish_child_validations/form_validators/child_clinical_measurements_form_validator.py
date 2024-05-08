from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import age, get_utcnow
from edc_constants.constants import FEMALE, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin
from ..utils import caregiver_subject_identifier


class ChildClinicalMeasurementsFormValidator(ChildFormValidatorMixin, FormValidator):
    child_assent_model = 'flourish_child.childassent'
    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    maternal_delivery_model = 'flourish_caregiver.maternaldelivery'

    def clean(self):

        cleaned_data = self.cleaned_data
        self.subject_identifier = cleaned_data.get(
            'child_visit').subject_identifier
        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_bp(cleaned_data)

        self.applicable_if_true(
            self.child_caregiver_consent_obj.gender == FEMALE and self.child_age >= 12,
            field_applicable='is_child_preg', )

        self.not_required_if(
            YES,
            field='is_child_preg',
            field_required='child_waist_circ')

        self.not_required_if(
            YES,
            field='is_child_preg',
            field_required='child_hip_circ')

        self.required_if_true(
            self.child_age >= 1.5,
            field_required='child_height',
        )

        self.required_if_true(
            self.child_age >= 1.5,
            field_required='child_weight_kg',
        )

        self.validate_skin_folds_measurements()

    def validate_skin_folds_measurements(self):
        measurements = [
            ('child_waist_circ', 'child_waist_circ_second', 'child_waist_circ_third'),
            ('child_hip_circ', 'child_hip_circ_second', 'child_hip_circ_third'),
            ('skin_folds_triceps', 'skin_folds_triceps_second',
             'skin_folds_triceps_third'),
            ('skin_folds_subscapular', 'skin_folds_subscapular_second',
             'skin_folds_subscapular_third'),
            ('skin_folds_suprailiac', 'skin_folds_suprailiac_second',
             'skin_folds_suprailiac_third'), ]

        for fields in measurements:
            self.validate_measurement_margin(*fields)
            for field in fields:
                if 'skin_folds' in field and 'third' not in field:
                    visit_skin_fold_messure = self.cleaned_data.get(
                        'visit_skin_fold_messure')
                    field_required = self.cleaned_data.get(field)
                    if (visit_skin_fold_messure == YES and (
                            not field_required or field_required == '')):
                        msg = {field: 'This field is required.'}
                        raise ValidationError(msg)

    def validate_bp(self, cleaned_data):
        child_systolic_bp = cleaned_data.get('child_systolic_bp')
        child_diastolic_bp = cleaned_data.get('child_diastolic_bp')

        if self.child_age >= 4:
            if not child_systolic_bp:
                msg = {'child_systolic_bp': 'This field is required.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            if not child_diastolic_bp:
                msg = {'child_diastolic_bp': 'This field is required.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        elif self.child_age < 4:
            if child_systolic_bp:
                msg = {'child_systolic_bp': 'This field is not required.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            if child_diastolic_bp:
                msg = {'child_diastolic_bp': 'This field is not required.'}
                self._errors.update(msg)
                raise ValidationError(msg)

        if child_systolic_bp and child_diastolic_bp:
            if child_systolic_bp < child_diastolic_bp:
                msg = {'child_diastolic_bp':
                           'Systolic blood pressure cannot be lower than the '
                           'diastolic blood pressure. Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_measurement_margin(self, first_measurement_field,
                                    second_measurement_field, third_measurement_field):
        first_measurement = self.cleaned_data.get(first_measurement_field, None)
        second_measurement = self.cleaned_data.get(second_measurement_field, None)

        if first_measurement and second_measurement:
            margin = abs(first_measurement - second_measurement)
            self.required_if_true(
                margin >= 1,
                field_required=third_measurement_field
            )

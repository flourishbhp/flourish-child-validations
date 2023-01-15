from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import get_utcnow, age
from edc_constants.constants import FEMALE, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildClinicalMeasurementsFormValidator(ChildFormValidatorMixin, FormValidator):
    child_assent_model = 'flourish_child.childassent'

    child_caregiver_consent_model = 'flourish_caregiver.caregiverchildconsent'

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

        self.validate_skin_folds_followup()

        measurements = [('child_waist_circ', 'child_waist_circ_second', 'child_waist_circ_third'),
                        ('child_hip_circ', 'child_hip_circ_second', 'child_hip_circ_third'),
                        ('skin_folds_triceps', 'skin_folds_triceps_second', 'skin_folds_triceps_third'),
                        ('skin_folds_subscapular', 'skin_folds_subscapular_second', 'skin_folds_subscapular_third'),
                        ('skin_folds_suprailiac', 'skin_folds_suprailiac_second', 'skin_folds_suprailiac_third'), ]

        for fields in measurements:
            self.validate_measurement_margin(*fields)

    def validate_skin_folds_followup(self):

        child_visit = self.cleaned_data.get('child_visit')

        req_fields = ['skin_folds_triceps', 'skin_folds_subscapular', 'skin_folds_suprailiac']

        for req_field in req_fields:
            self.required_if_true(
                child_visit.visit_code == '3000',
                field_required=req_field,
                inverse=False)

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

    @property
    def child_assent_obj(self):
        child_assent_model_cls = django_apps.get_model(self.child_assent_model)
        try:
            model_obj = child_assent_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except child_assent_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def child_caregiver_consent_obj(self):
        child_caregiver_consent_model_cls = django_apps.get_model(
            self.child_caregiver_consent_model)
        try:
            model_obj = child_caregiver_consent_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except child_caregiver_consent_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def maternal_delivery_obj(self):
        maternal_delivery_model_cls = django_apps.get_model(
            self.maternal_delivery_model)
        try:
            model_obj = maternal_delivery_model_cls.objects.get(
                subject_identifier__istartswith=self.subject_identifier)
        except maternal_delivery_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def child_age(self):

        if self.child_assent_obj:
            birth_date = self.child_assent_obj.dob
            years = age(birth_date, get_utcnow()).years
            return years
        elif self.child_caregiver_consent_obj:
            birth_date = self.child_caregiver_consent_obj.child_dob
            years = age(birth_date, get_utcnow()).years
            return years
        elif self.maternal_delivery_obj:
            birth_date = self.maternal_delivery_obj.delivery_datetime.date()
            years = age(birth_date, get_utcnow()).months
            return years
        return 0

    def validate_measurement_margin(self, first_measurement_field, second_measurement_field, third_measurement_field):
        first_measurement = self.cleaned_data.get(first_measurement_field, None)
        second_measurement = self.cleaned_data.get(second_measurement_field, None)

        if first_measurement and second_measurement:
            margin = abs(first_measurement - second_measurement)
            self.required_if_true(
                margin >= 1,
                field_required=third_measurement_field
            )

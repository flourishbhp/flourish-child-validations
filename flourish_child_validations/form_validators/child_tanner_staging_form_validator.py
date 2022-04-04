from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, YES, FEMALE, MALE
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTannerStagingFormValidator(ChildFormValidatorMixin, FormValidator):
    child_assent_model = 'flourish_child.childassent'

    @property
    def child_assent_model_cls(self):
        return django_apps.get_model(self.child_assent_model)

    def clean(self):
        super().clean()
        report_datetime = self.cleaned_data.get('report_datetime')

        subject_identifier = self.cleaned_data.get('child_visit').subject_identifier

        self.validate_consent_version_obj(subject_identifier)

        self.validate_against_visit_datetime(report_datetime)

        self.validate_child_gender()

        self.required_if(
            NO,
            field='assessment_done',
            field_required='reasons_not_done')

        fields = ['child_gender', 'pubic_hair_stage']
        for field in fields:
            self.applicable_if(
                YES,
                field='assessment_done',
                field_applicable=field)

        not_required = ['rgt_testclr_vol', 'lft_testclr_vol']
        for field in not_required:
            self.not_required_if(
                NO,
                field='assessment_done',
                field_required=field,
                inverse=False)

        female_fields = ['breast_stage', 'manarche_dt_avail']
        for field in female_fields:
            self.applicable_if(
                FEMALE,
                field='child_gender',
                field_applicable=field)

        self.required_if(
            YES,
            field='manarche_dt_avail',
            field_required='menarche_dt')

        self.applicable_if(
            YES,
            field='manarche_dt_avail',
            field_applicable='menarche_dt_est')

        male_fields = ['male_gen_stage', 'testclr_vol_measrd']
        for field in male_fields:
            self.applicable_if(
                MALE,
                field='child_gender',
                field_applicable=field)

        vol_fields = ['rgt_testclr_vol', 'lft_testclr_vol']
        for field in vol_fields:
            self.required_if(
                YES,
                field='testclr_vol_measrd',
                field_required=field)

    def validate_child_gender(self):
        assent = self.child_assent_model_obj()
        gender = self.cleaned_data.get('child_gender')
        if assent:
            if gender != assent.gender:
                msg = {'child_gender':
                           f'Child gender does not match `{assent.gender}` from '
                           'the Assent form. Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def child_assent_model_obj(self):
        subject_identifier = self.cleaned_data.get('child_visit').subject_identifier
        try:
            assent = self.child_assent_model_cls.objects.get(
                subject_identifier=subject_identifier)
        except self.child_assent_model_cls.DoesNotExist:
            return None
        else:
            return assent

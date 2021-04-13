from edc_constants.constants import NO, YES, FEMALE, MALE
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTannerStagingFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        report_datetime = self.cleaned_data.get('report_datetime')

        self.validate_against_visit_datetime(report_datetime)

        self.required_if(
            NO,
            field='assessment_done',
            field_required='reasons_not_done')

        not_applicable = ['breast_stage', 'manarche_dt_avail', 'menarche_dt_est',
                          'male_gen_stage', 'testclr_vol_measrd']
        for field in not_applicable:
            self.not_applicable_only_if(
                NO,
                field='assessment_done',
                field_applicable=field)

        not_required = ['menarche_dt', 'rgt_testclr_vol', 'lft_testclr_vol']
        for field in not_required:
            self.not_required_if(
                NO,
                field='assessment_done',
                field_required=field,
                inverse=False)

        fields = ['child_gender', 'pubic_hair_stage']
        for field in fields:
            self.applicable_if(
                YES,
                field='assessment_done',
                field_applicable=field)

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

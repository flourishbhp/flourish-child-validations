from django.apps import apps as django_apps
from django.forms import ValidationError
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, YES
from edc_form_validators import FormValidator


from .form_validator_mixin import ChildFormValidatorMixin


def check_values(queryset, values):
    return {value: any(value in str(item) for item in queryset) for value in
            values}


class ChildTBReferralOutcomeFormValidator(ChildFormValidatorMixin, FormValidator):

    tb_referral_model = 'flourish_child.childtbreferral'
    tb_referral_outcome_model = 'flourish_child.childtbreferraloutcome'

    @property
    def tb_referral_model_cls(self):
        return django_apps.get_model(self.tb_referral_model)

    @property
    def tb_referral_outcome_model_cls(self):
        return django_apps.get_model(self.tb_referral_outcome_model)

    def clean(self):
        super().clean()

        self.validate_outcomes_exists_for_referral()

        self.required_if(
                YES,
                field='tb_evaluation',
                field_required='clinic_name'
            )

        queryset = self.cleaned_data.get('tests_performed')
        value_checks = check_values(queryset,
                                    ['Sputum sample', 'other', 'Chest Xray',
                                     'Stool sample', 'Urine test', 'Skin test',
                                     'Blood test'])

        self.m2m_single_selection_if('none', m2m_field='tests_performed')

        for value, exists in value_checks.items():
            self.required_if_true(exists,
                                  f'{value.lower().replace(" ", "_")}_results')
            if value == 'other':
                self.required_if_true(exists, 'other_test_specify')
                self.required_if_true(exists, 'other_test_results')

        self.required_if(
            YES,
            field='tb_evaluation',
            field_required='evaluated',
        )

        required_fields = ['tests_performed', 'diagnosed_with_tb', ]
        for field in required_fields:
            self.required_if(
                    YES,
                    field='evaluated',
                    field_required=field
                )
        self.required_if(
            NO,
            field='evaluated',
            field_required='reason_not_evaluated',
        )
        self.validate_other_specify(
            field='reason_not_evaluated',
            other_specify_field='reason_not_evaluated_other'
        )

        self.validate_other_specify(
            field='clinic_name',
            other_specify_field='clinic_name_other'
        )

        self.required_if(
            NO,
            field='diagnosed_with_tb',
            field_required='tb_preventative_therapy'
        )

        self.validate_other_specify(
            field='tb_treatment',
            other_specify_field='other_tb_treatment'
        )

        self.validate_other_specify(
            field='tb_preventative_therapy',
            other_specify_field='other_tb_preventative_therapy'
        )

        self.required_if(
            NO,
            field='tb_evaluation',
            field_required='reasons',
        )

        self.required_if(YES,
                         field='diagnosed_with_tb',
                         field_required='tb_treatment')

        self.validate_other_specify(
            field='reasons',
            other_specify_field='other_reasons'
        )

        self.validate_results_tb_treatment_and_prevention()

    def validate_results_tb_treatment_and_prevention(self):
        tb_treatment = self.cleaned_data.get('tb_treatment')
        diagnosed_with_tb = self.cleaned_data.get('diagnosed_with_tb')

        if tb_treatment != YES and diagnosed_with_tb == YES:
            raise ValidationError({
                'tb_treatment': 'If any diagnosed with tb , this field must be Yes',
            })

    def validate_outcomes_exists_for_referral(self):
        """ Check if there's already an outcome completed for the related referral
        """
        report_datetime = self.cleaned_data.get('report_datetime', None)
        try:
            related_referral = self.tb_referral_model_cls.objects.filter(
                child_visit__subject_identifier=self.subject_identifier,
                report_datetime__lt=report_datetime).latest('report_datetime')
        except self.tb_referral_model_cls.DoesNotExist:
            pass
        else:
            referral_dt = getattr(related_referral, 'report_datetime', None)

            referral_outcome = self.tb_referral_outcome_model_cls.objects.filter(
                child_visit__subject_identifier=self.subject_identifier,
                report_datetime__range=(referral_dt, get_utcnow()))
            if self.instance:
                referral_outcome = referral_outcome.exclude(id=self.instance.id)
            if referral_outcome.exists():
                visit_code = referral_outcome.first().visit_code
                raise ValidationError(
                    {'__all__':
                     f'Referral outcome already completed at visit {visit_code}'})

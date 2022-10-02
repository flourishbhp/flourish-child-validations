from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import get_utcnow
from edc_constants.constants import NO , YES, NOT_APPLICABLE
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildPregTestingFormValidator(ChildFormValidatorMixin, FormValidator):

    child_caregiver_consent_model = 'flourish_caregiver.caregiverchildconsent'

    def clean(self):

        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        visit_code = self.cleaned_data.get('child_visit').visit_code

        self.required_if_true(visit_code == '2000',
                              field_required='test_done',
                              inverse=False)

        all_fields = ['last_menstrual_period', 'is_lmp_date_estimated']

        for field in all_fields:
            self.required_if(YES, field='menarche', field_required=field)

        test_done_fields = ['test_date', 'preg_test_result', ]
        for field in test_done_fields:
            self.required_if(YES, field='test_done', field_required=field)

        self.required_if_not_none(field='last_menstrual_period',
                                  field_required='is_lmp_date_estimated')

        self.validate_consent_version_obj(self.subject_identifier)
        self.validate_lmp()

    @property
    def child_caregiver_consent_model_cls(self):
        return django_apps.get_model(self.child_caregiver_consent_model)

    @property
    def caregiver_child_obj(self):

        caregiver_chld_consents = self.child_caregiver_consent_model_cls.objects.filter(
                subject_identifier=self.subject_identifier)

        if caregiver_chld_consents:
            return caregiver_chld_consents.latest('consent_datetime')

    def validate_lmp(self):
        """A function to validate the lmp if it is below the 2months threshold
        and if it is then the pregnancy test is required
        """
        threshold_date = (get_utcnow() - relativedelta(months=2)).date()
        lmp = self.cleaned_data.get('last_menstrual_period')
        consent = self.caregiver_child_obj
        today_dt = get_utcnow().date()
        childvisit = self.cleaned_data.get('child_visit')
        test_done = self.cleaned_data.get('test_done')
        menarche = self.cleaned_data.get('menarche')

        if consent:
            if any(item in childvisit.schedule_name for item in ['qt', 'quart']):
                if menarche == YES:
                    if lmp:
                        if lmp == today_dt:
                            message = {'last_menstrual_period': (
                                'Last Menstrual Period date cannot be today.')}
                            self._errors.update(message)
                            raise ValidationError(message)
                        elif lmp <= threshold_date and test_done != YES:
                                message = {'test_done': 'A pregnancy test is needed'}
                                self._errors.update(message)
                                raise ValidationError(message)

                    else:
                        message = {'last_menstrual_period': (
                            'Last Menstrual Period date cannot be left blank.')}
                        self._errors.update(message)
                        raise ValidationError(message)

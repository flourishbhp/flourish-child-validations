from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildPregTestingFormValidator(ChildFormValidatorMixin, FormValidator):
    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    child_preg_testing_model = 'flourish_child.childpregtesting'
    tanner_staging_model = 'flourish_child.childtannerstaging'

    def clean(self):

        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.required_if(YES,
                         field='menarche',
                         field_required='menarche_start_dt')

        menarche_start_dt = self.cleaned_data.get('menarche_start_dt', None)
        self.applicable_if_true(
            bool(menarche_start_dt),
            field_applicable='menarche_start_est', )

        self.applicable_if(YES,
                           field='menarche',
                           field_applicable='experienced_pregnancy')

        self.validate_lmp_required()

        self.required_if_not_none(field='last_menstrual_period',
                                  field_required='is_lmp_date_estimated')

        test_done_fields = ['test_date', 'preg_test_result', ]
        for field in test_done_fields:
            self.required_if(YES,
                             field='test_done',
                             field_required=field)

        self.validate_consent_version_obj(self.subject_identifier)
        self.validate_lmp()

    @property
    def child_caregiver_consent_model_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    @property
    def child_preg_testing_model_cls(self):
        return django_apps.get_model(self.child_preg_testing_model)

    @property
    def child_visit(self):
        return self.cleaned_data.get('child_visit', None)

    @property
    def tanner_staging_model_cls(self):
        return django_apps.get_model(self.tanner_staging_model)

    @property
    def caregiver_child_obj(self):

        caregiver_chld_consents = self.child_caregiver_consent_model_cls.objects.filter(
            subject_identifier=self.subject_identifier)

        if caregiver_chld_consents:
            return caregiver_chld_consents.latest('consent_datetime')

    def validate_lmp_required(self):
        """ Require lmp date if participant is pregnant, or has reached menarche, and it
            is not the first time.
        """
        experienced_preg = self.cleaned_data.get('experienced_pregnancy', '') == YES
        stated_menarche = self.cleaned_data.get('menarche') == YES

        if self.prev_objs:
            not_first_start = self.prev_objs.menarche == NO 
        else:
            not_first_start = self.tanner_staging_objs.exists()
        
        self.required_if_true(
            experienced_preg or (stated_menarche and not_first_start),
            field_required='last_menstrual_period', )

    def validate_lmp(self):
        """A function to validate the lmp if it is below the 2months threshold
        and if it is then the pregnancy test is required
        """
        threshold_date = (get_utcnow() - relativedelta(months=2)).date()
        lmp = self.cleaned_data.get('last_menstrual_period', None)
        consented = self.caregiver_child_obj
        today_dt = get_utcnow().date()
        menarche_start_dt = self.cleaned_data.get('menarche_start_dt', None)
        experienced_pregnancy = self.cleaned_data.get('experienced_pregnancy', None)

        if consented:
            if lmp and (lmp == today_dt):
                message = {'last_menstrual_period':
                           'Last Menstrual Period date cannot be today.'}
                self._errors.update(message)
                raise ValidationError(message)
            if lmp and (lmp < menarche_start_dt):
                message = {'last_menstrual_period':
                           'Date of LMP can not be before start of menarche.'}
                self._errors.update(message)
                raise ValidationError(message)

            lmp_condition = (experienced_pregnancy == NO) or (
                    lmp and lmp <= threshold_date)
            self.applicable_if_true(
                lmp_condition,
                field_applicable='test_done',
                applicable_msg='A pregnancy test is needed')

    @property
    def prev_objs(self):
        child_visit = self.cleaned_data.get('child_visit', None)

        child_visit = getattr(child_visit, 'previous_visit', None)

        try:
            previous_menarche = self.child_preg_testing_model_cls.objects.get(
                child_visit=child_visit)
        except self.child_preg_testing_model_cls.DoesNotExist:
            return None
        else:
            return previous_menarche


    @property
    def tanner_staging_objs(self):
        return self.tanner_staging_model_cls.objects.filter(
            manarche_dt_avail=YES,
            child_visit__subject_identifier=self.child_visit.subject_identifier)

from django import forms
from django.apps import apps as django_apps
from edc_constants.constants import NEW, NO
from edc_base.utils import get_utcnow

from edc_action_item.site_action_items import site_action_items
from flourish_prn.action_items import CHILDOFF_STUDY_ACTION


class CrfOffStudyFormValidator:

    def clean(self):
        if self.instance and not self.instance.id:
            self.validate_offstudy_model()
        super().clean()

    def validate_offstudy_model(self):
        report_datetime = self.cleaned_data.get('report_datetime', get_utcnow())
        child_offstudy_cls = django_apps.get_model(
            'flourish_prn.childoffstudy')
        action_cls = site_action_items.get(
            child_offstudy_cls.action_name)
        action_item_model_cls = action_cls.action_item_model_cls()

        self.child_visit = self.cleaned_data.get('child_visit') or None

        try:
            action_item_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                action_type__name=CHILDOFF_STUDY_ACTION,
                status=NEW)
        except action_item_model_cls.DoesNotExist:
            try:
                child_offstudy_cls.objects.get(
                    subject_identifier=self.subject_identifier,
                    offstudy_date__lt=report_datetime.date())
            except child_offstudy_cls.DoesNotExist:
                pass
            else:
                raise forms.ValidationError(
                    'Participant has been taken offstudy. Cannot capture any '
                    'new data.')
        else:
            if not self.child_visit or self.child_visit.require_crfs == NO:
                raise forms.ValidationError(
                    'Participant is scheduled to be taken offstudy without '
                    'any new data collection. Cannot capture any new data.')

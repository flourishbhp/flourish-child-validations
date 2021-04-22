from django.apps import apps as django_apps
from edc_form_validators import FormValidator


class AcademicPerformanceFormValidator(FormValidator):

    child_socio_demographic_model = 'flourish_child.childsociodemographic'

    @property
    def child_socio_demographic_cls(self):
        return django_apps.get_model(self.child_socio_demographic_model)

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        super().clean()

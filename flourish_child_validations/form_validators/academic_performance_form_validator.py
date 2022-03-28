from django.apps import apps as django_apps
from edc_form_validators import FormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class AcademicPerformanceFormValidator(ChildFormValidatorMixin, FormValidator):

    child_socio_demographic_model = 'flourish_child.childsociodemographic'

    @property
    def child_socio_demographic_cls(self):
        return django_apps.get_model(self.child_socio_demographic_model)

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)

        self.required_if(
            'points',
            field='overall_performance',
            field_required='grade_points')

        super().clean()

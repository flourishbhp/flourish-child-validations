from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildReferralFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_other_specify(field='referred_to')

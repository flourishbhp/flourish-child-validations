from edc_form_validators import FormValidator
from ..form_validator_mixin import ChildFormValidatorMixin


class TbReferralAdolFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.validate_other_specify(
            field='location',
            other_specify_field='location_other', )

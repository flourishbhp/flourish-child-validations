from flourish_form_validations.form_validators.cage_aid_form_validator_mixin import CageAidFormValidatorMixin
from .form_validator_mixin import ChildFormValidatorMixin


class ChildCageAidFormValidator(CageAidFormValidatorMixin, ChildFormValidatorMixin):

    def clean(self):
        super().clean()

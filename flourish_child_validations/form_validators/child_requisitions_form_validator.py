from edc_constants.constants import YES
from edc_form_validators import FormValidator


class ChildRequisitionsFormValidations(FormValidator):
    def clean(self):
        super().clean()

        required_fields = ['item_count', 'estimated_volume']

        for field in required_fields:
            self.required_if(YES,
                             field='is_drawn',
                             field_required=field)

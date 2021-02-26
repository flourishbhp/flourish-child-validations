from edc_constants.constants import OTHER
from edc_form_validators import FormValidator


class ChildPerformanceFormValidator(FormValidator):

    def clean(self):

        self.validate_other_specify(field='education_level',
                                    other_specify_field='education_level_other'
                                    )

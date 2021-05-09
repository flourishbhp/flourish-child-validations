from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator
from edc_constants.constants import NO


class ChildPregTestingFormValidator(FormValidator):

    def clean(self):
        test_done = self.cleaned_data.get('test_done')
        if test_done == NO:
            message = {'test_done':
                       'A pregnancy test is needed'}
            self._errors.update(message)
            raise ValidationError(message)

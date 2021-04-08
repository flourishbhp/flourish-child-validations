from edc_constants.constants import YES
from edc_form_validators import FormValidator


class ChildHIVRapidTestValidator(FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').subject_identifier
        super().clean()

        self.required_if(
            YES,
            field='rapid_test_done',
            field_required='result_date',
            required_msg=('If a rapid test was processed, what is '
                          f'the result date of the rapid test?'),
            not_required_msg=('If a rapid test was not processed, '
                              f'please do not provide the result date.'))

        self.required_if(
            YES,
            field='rapid_test_done',
            field_required='result',
            required_msg=('If a rapid test was processed, what is '
                          f'the result of the rapid test?'),
            not_required_msg=('If a rapid test was not processed, '
                              f'please do not provide the result.'))

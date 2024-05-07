from edc_form_validators import FormValidator
from edc_constants.constants import YES, POS
from ..form_validator_mixin import ChildFormValidatorMixin


class HIVTestingFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        '''
        'test_for_hiv',
        'times_tested',
        'last_result',
        'referred_for_treatment',
        'initiated_treatment',
        'date_initiated_treatment',
        'seen_by_healthcare',
        '''

        hiv_required_fields = ['times_tested', 'last_result']

        for field in hiv_required_fields:
            self.required_if(YES,
                             field='test_for_hiv',
                             field_required=field)

        fields = [
            'referred_for_treatment',
            'initiated_treatment',
            'seen_by_healthcare',
        ]

        for field in fields:
            self.required_if(POS,
                             field='last_result',
                             field_required=field)

        self.required_if(YES,
                         field='initiated_treatment',
                         field_required='date_initiated_treatment')

from edc_constants.constants import YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTBScreeningFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        required_fields = ['cough', 'fever', 'sweats', 'weight_loss']

        for field in required_fields:
            self.required_if(YES,
                             field=field,
                             field_required=f'{field}_duration')

        self.required_if(YES,
                         field='evaluated_for_tb',
                         field_required='clinic_visit_date')

        self.validate_other_specify(
            field='tb_tests',
            other_specify_field='other_test',
        )

        self.required_if('chest_xray',
                         field='tb_tests',
                         field_required='chest_xray_results')

        self.required_if('sputum_sample',
                         field='tb_tests',
                         field_required='sputum_sample_results')

        self.required_if('stool_sample',
                         field='tb_tests',
                         field_required='stool_sample_results')

        self.required_if('urine_test',
                         field='tb_tests',
                         field_required='urine_test_results')

        self.required_if('skin_test',
                         field='tb_tests',
                         field_required='skin_test_results')

        self.required_if('blood_test',
                         field='tb_tests',
                         field_required='blood_test_results')

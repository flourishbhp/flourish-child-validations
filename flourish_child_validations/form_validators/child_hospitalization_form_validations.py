from edc_constants.constants import YES
from edc_form_validators import FormValidator


class ChildHospitalizationFormValidations(FormValidator):

    def clean(self):
        super().clean()

        self.required_if(
            YES,
            field='hospitalized',
            field_required='number_hospitalised'
        )


class AdmissionsReasonFormValidations(FormValidator):

    def clean(self):
        super().clean()

        self.validate_other_specify('hospital_name')

        self.required_if(
            'surgical',
            field='reason',
            field_required='reason_surgical'
        )

        self.validate_other_specify('reason')

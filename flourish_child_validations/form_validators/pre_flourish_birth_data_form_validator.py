from edc_form_validators import FormValidator


class PreFlourishBirthDataFormValidator(FormValidator):

    def clean(self):
        self.required_if('yes_weeks',
                         field='gestational_age_known',
                         field_required='gestational_age_weeks')

        self.required_if('yes_months',
                         field='gestational_age_known',
                         field_required='gestational_age_months')

        self.validate_other_specify(
            field='place_of_birth',
            other_specify_field='other_place_of_birth',
        )

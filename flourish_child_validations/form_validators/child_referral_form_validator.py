from edc_form_validators import FormValidator


class ChildReferralFormValidator(FormValidator):

    def clean(self):

        self.validate_other_specify(field='referred_to')

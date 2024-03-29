from django import forms
from edc_constants.constants import YES, NO
from edc_form_validators.form_validator import FormValidator


class YoungAdultLocatorFormValidator(FormValidator):

    def clean(self):
        super().clean()
        fields = ['may_visit_home', 'may_call',
                  'may_call_work', 'may_contact_indirectly']

        for field in fields:

            self.required_if(NO,
                             field='along_side_caregiver',
                             field_required=field)

        self.required_if(
            YES,
            field='may_visit_home',
            field_required='physical_address')

        self.required_if(YES, field='may_call', field_required='subject_cell')

        self.validate_may_call_fields()
        self.validate_work_contact()
        self.validate_contact_details()
        self.validate_indirect_contact()

    def validate_work_contact(self):
        self.required_if(
            YES, field='may_call_work', field_required='subject_work_place')
        self.not_required_if(
            NO, field='may_call_work',
            field_required='subject_work_phone', inverse=False)
        self.not_required_if(
            NO, field='may_call_work',
            field_required='subject_work_cell', inverse=False)

    def validate_contact_details(self):
        self.required_if(
            YES, field='home_visit_permission', field_required='physical_address')
        self.required_if(
            YES, field='may_contact_someone', field_required='contact_name')
        self.required_if(
            YES, field='contact_name', field_required='contact_rel')
        self.required_if(
            YES, field='contact_name', field_required='contact_physical_address')

    def validate_indirect_contact(self):
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_name')
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_relation')
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_physical_address')
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_cell')

        for field in ['indirect_contact_cell_alt', 'indirect_contact_phone']:
            self.not_required_if(
                NO, field='may_contact_indirectly', field_required=field,
                inverse=False)

    def validate_may_call_fields(self):
        validations = {}
        number_fields = ['subject_cell', 'subject_phone']
        if self.cleaned_data.get('may_call') == YES:
            if all([self.cleaned_data.get(f) is None for f in number_fields]):
                validations = {
                    k: 'This field is required' for k in number_fields}
        elif self.cleaned_data.get('may_call') == NO:
            number_fields.extend(['subject_cell_alt', 'subject_phone_alt']),
            for field in number_fields:
                if self.cleaned_data.get(field):
                    validations.update({field: 'This field is not required.'})
        if validations:
            raise forms.ValidationError(validations)

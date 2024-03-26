from django.core.exceptions import ValidationError
from edc_constants.constants import OTHER, UNKNOWN, YES
from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class InfantArvExposureFormValidator(ChildFormValidatorMixin,
                                     CrfOffStudyFormValidator,
                                     FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))

        fields_required = {
            'azt_dose_date': (
                'Provide date of the first dose for AZT.',
                'Participant indicated that AZT was NOT provided. '
                'You cannot provide date of first dose'),
            'azt_within_72h': (
                'Please specify if AZT dosing occurred within 72 hours of birth',
                'AZT was NOT provided. Question is not required.')}

        for field, messages in fields_required.items():
            self.required_if(
                YES,
                field='azt_after_birth',
                field_required=field,
                required_msg=messages[0],
                not_required_msg=messages[1])

        if (self.cleaned_data.get('azt_after_birth')
                and self.cleaned_data.get('azt_after_birth') == UNKNOWN):
            if self.cleaned_data.get('azt_additional_dose') != UNKNOWN:
                msg = {'azt_additional_dose': 'If Q3 is \'Unknown\', '
                                              'this field must be \'Unknown.\''}
                self._errors.update(msg)
                raise ValidationError(msg)
        else:
            self.applicable_if(
                YES,
                field='azt_after_birth',
                field_applicable='azt_additional_dose')

        fields_required = {
            'nvp_dose_date': (
                'If infant has received single dose NVP then provide NVP date.',
                'Participant indicated that NVP was NOT provided. '
                'You cannot provide date of first dose'),
            'snvp_dose_within_72h': (
                'Please specify if NVP single dosing occurred within 72 hours of birth',
                'NVP was NOT provided. Question is not required.')}

        for field, messages in fields_required.items():
            self.required_if(
                YES,
                field='sdnvp_after_birth',
                field_required=field,
                required_msg=messages[0],
                not_required_msg=messages[1])

        fields_required = ['arvs_specify', 'date_1st_arv_dose']
        for field in fields_required:
            self.required_if(YES,
                             field='additional_arvs',
                             field_required=field)

        self.required_if(OTHER,
                         field='arvs_specify',
                         field_required='arvs_specify_other')

    def validate_nvp_cont_dosing(self):
        nvp_cont_dosing = self.cleaned_data('nvp_cont_dosing')
        sdnvp_after_birth = self.cleaned_data('sdnvp_after_birth')

        if (not (nvp_cont_dosing == UNKNOWN or nvp_cont_dosing == YES) and
                sdnvp_after_birth == YES):
            raise ValidationError({
                'nvp_cont_dosing': 'This Question can only be NO if the child did not  '
                                   'received NVP after birth'
            })

from edc_constants.constants import ABNORMAL, NO
from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class BirthExamFormValidator(ChildFormValidatorMixin, CrfOffStudyFormValidator,
                             FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))

        self.required_if(
            ABNORMAL,
            field='general_activity',
            field_required='abnormal_activity',
            required_msg='If abnormal, please specify.',
            not_required_msg=('You indicated that there was NO abnormality in '
                              'general activity, yet specified abnormality. '
                              'Please correct')
        )

        responses = (NO, 'Not_evaluated')
        self.required_if(
            *responses,
            field='heent_exam',
            field_required='heent_no_other',
            required_msg=('You indicated that HEENT exam was not normal'
                          '/not evaluated. Provide answer to Q7.'))

        self.required_if(
            *responses,
            field='resp_exam',
            field_required='resp_exam_other',
            required_msg=('You indicated that Respiratory exam was not normal'
                          '/not evaluated. Provide answer to Q9.'))

        self.required_if(
            *responses,
            field='cardiac_exam',
            field_required='cardiac_exam_other',
            required_msg=('You indicated that Cardiac exam was not normal'
                          '/not evaluated. Provide answer to Q11.'))

        self.required_if(
            *responses,
            field='abdominal_exam',
            field_required='abdominal_exam_other',
            required_msg=('You indicated that Abdominal exam was not normal'
                          '/not evaluated. Provide answer to Q13.'))

        self.required_if(
            *responses,
            field='skin_exam',
            field_required='skin_exam_other',
            required_msg=('You indicated that Skin exam was not normal'
                          '/not evaluated. Provide answer to Q15.'))

        self.required_if(
            *responses,
            field='neurologic_exam',
            field_required='neuro_exam_other',
            required_msg=('You indicated that Neurological exam was not normal'
                          '/not evaluated. Provide answer to Q19.'))

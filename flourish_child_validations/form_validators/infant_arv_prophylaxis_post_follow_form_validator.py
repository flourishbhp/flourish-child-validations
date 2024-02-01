from django.core.exceptions import ValidationError
from edc_constants.constants import NO, YES
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators.child_visit_form_validator import \
    ChildFormValidatorMixin


class InfantArvProphylaxisPostFollowFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.m2m_required_if(
            response=YES,
            field='prophylactic_med_last_visit',
            m2m_field='arv_status', )

        self.m2m_required_if(
            response=NO,
            field='prophylactic_med_last_visit',
            m2m_field='reason_no_art', )

        self.m2m_other_specify_applicable(
            field_other='reason_no_art_other',
            m2m_field='reason_no_art',
        )

        self.validate_field_required_m2m(
            field='days_completed',
            response='after_28_days',
            m2m_field='arv_status',
        )

        self.validate_field_required_m2m(
            field='arv_status_incomplete_reason',
            response='incomplete',
            m2m_field='arv_status',
        )

        q_and_follow = {
            'NVP': ['nvp_start_date', 'nvp_end_date'],
            'AZT': ['azt_start_date', 'azt_end_date'],
            '3TC': ['start_date_3tc', 'end_date_3tc'],
            'FTC': ['start_date_ftc', 'end_date_ftc'],
            'ALU': ['alu_start_date', 'alu_end_date'],
            'TRV': ['trv_start_date', 'trv_end_date'],
            'TDF': ['tdf_start_date', 'tdf_end_date'],
            'ABC': ['abc_start_date', 'abc_end_date'],
            'RAL': ['ral_start_date', 'ral_end_date'],
        }

        for key, value in q_and_follow.items():
            for field in value:
                self.validate_field_required_m2m(
                    field=field,
                    response=key,
                    m2m_field='arv_status',
                )

        self.required_if(
            YES,
            field='modification_starting_arv',
            field_required='modification_date',
        )

        self.m2m_required_if(
            response=YES,
            field='modification_starting_arv',
            m2m_field='modification_reason',
        )

        self.validate_field_required_m2m(
            field='modification_reason_side_effects',
            response='side_effects',
            m2m_field='modification_reason',
        )

        self.m2m_other_specify_applicable(
            field_other='modification_reason_other',
            m2m_field='modification_reason',
        )

        missed_dose_questions = ['missed_dose_count', 'reason_missed']

        for field in missed_dose_questions:
            self.required_if(
                YES,
                field=field,
                field_required='missed_dose',
            )

        super().clean()

    def validate_field_required_m2m(self, field, response, m2m_field):
        m2m_field_responses = self.cleaned_data.get(f'{m2m_field}')
        if m2m_field_responses and m2m_field_responses.count() > 0:
            selected = {obj.short_name: obj.name for obj in m2m_field_responses}
            field = self.cleaned_data.get(f'{field}')
            if response in selected and not field:
                self._errors.update({f'{field}': 'This field is required.'})
                self._error_codes.append('required')
                raise ValidationError('This field is required.', code='required')

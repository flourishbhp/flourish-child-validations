from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class InfantCongenitalAnomaliesFormValidator(ChildFormValidatorMixin,
                                             CrfOffStudyFormValidator,
                                             FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))


class InfantFacialDefectFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='facial_defect',
            other_specify_field='facial_defects_other')


class InfantCleftDisorderFormFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='cleft_disorder',
            other_specify_field='cleft_disorders_other')


class InfantMouthUpGiFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='mouth_up_gi')


class InfantCardioDisorderFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='cardio_disorder',
            other_specify_field='cardiovascular_other')


class InfantRespiratoryDefectFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='respiratory_defect',
            other_specify_field='respiratory_defects_other')


class InfantLowerGiFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='lower_gi')


class InfantFemaleGenitalFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='female_genital')


class InfantMaleGenitalFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='male_genital')


class InfantRenalFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='renal')


class InfantMusculoskeletalFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='musculo_skeletal')


class InfantSkinFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='skin')


class InfantTrisomiesFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='trisomies')


class InfantCnsFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='cns')

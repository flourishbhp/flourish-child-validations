from edc_form_validators import FormValidator
from edc_constants.constants import OTHER
from ..form_validator_mixin import ChildFormValidatorMixin


class TbKnowledgeFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.m2m_other_specify(OTHER,
                               m2m_field='tb_knowledge_medium',
                               field_other='tb_knowledge_medium_other')

        self.required_if(OTHER,
                         field='tb_community_treatment',
                         field_required='tb_community_treatment_other')

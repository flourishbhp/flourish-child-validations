from unittest.mock import MagicMock

from django.forms import ValidationError
from django.test import TestCase, tag

from flourish_child_validations.form_validators import \
    InfantArvProphylaxisPostFollowFormValidator
from flourish_child_validations.tests.models import ARTMedicationReasons


@tag('iapfu')
class TestInfantArvProphylaxisPostFollowFormValidator(TestCase):

    def setUp(self):
        m2m_relation_mock = MagicMock()
        m2m_relation_mock.all.return_value = ['NVP']
        m2m_relation_mock.count.return_value = 1
        self.form_data = {
            'arv_status': m2m_relation_mock,
            'last_visit': 'YES',
            'reason_no_art': m2m_relation_mock,
        }
        self.form = InfantArvProphylaxisPostFollowFormValidator(
            cleaned_data=self.form_data)

    def test_form_validator_with_missing_required_field(self):
        del self.form_data['arv_status']
        form_validator = InfantArvProphylaxisPostFollowFormValidator(
            cleaned_data=self.form_data)
        with self.assertRaises(ValidationError):
            form_validator.validate()

    def test_validate_field_required_m2m(self):

        m2m_relation = MagicMock()
        m2m_relation.count.return_value = 1
        m2m_relation.__iter__.return_value = iter(
            [MagicMock(short_name='NVP', name='NVP')])

        self.form.cleaned_data = {'arv_status': m2m_relation, 'nvp_start_date': None}
        validator = InfantArvProphylaxisPostFollowFormValidator(
            cleaned_data=self.form.cleaned_data)

        with self.assertRaises(ValidationError):
            validator.validate_field_required_m2m(field='nvp_start_date', response='NVP',
                                                  m2m_field='arv_status')

import unittest

from django.core.exceptions import ValidationError
from django.test import tag

from flourish_child_validations.form_validators import ChildTBScreeningFormValidator


class TestClass:
    def __init__(self, name, short_name):
        self.name = name
        self.short_name = short_name


@tag('child_tb_screening')
class TestChildTBScreeningFormValidator(unittest.TestCase):
    def test_required_if_m2m_response_no_field(self):
        cleaned_data = {'test_m2m_field': []}  # Empty m2m field
        instance = ChildTBScreeningFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError):
            instance.required_if_m2m('response', field='test_field', m2m_field='test_m2m_field')

    def test_required_if_m2m_response_with_field(self):
        m2m_mock = [TestClass(name='name', short_name='response')]
        cleaned_data = {'test_field': 'value', 'test_m2m_field': m2m_mock}
        instance = ChildTBScreeningFormValidator(cleaned_data=cleaned_data)
        try:
            instance.required_if_m2m('response', field='test_field', m2m_field='test_m2m_field')
        except ValidationError:
            self.fail("required_if_m2m raised ValidationError unexpectedly!")

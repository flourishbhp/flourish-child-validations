from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import (YES, NO, NEG, POS)

from ..form_validators import TbReferralOutcomesFormValidator
from .models import ListModel
from .test_model_mixin import TestModelMixin



@tag('tbref')
class TestTbReferralOutcomesFormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(TbReferralOutcomesFormValidator, *args, **kwargs)

    def setUp(self):

        ListModel.objects.bulk_create(
            objs=[ListModel(short_name='sputum', name='sputum'),
                  ListModel(short_name='chest_xray', name='chest_xray'),
                  ListModel(short_name='gene_xpert', name='gene_xpert'),
                  ListModel(short_name='tst_mantoux', name='tst_mantoux'),
                  ListModel(short_name='covid_19_test', name='covid_19_test')])

        self.data = {'tb_eval': 'Yes',
                     'reason_not_going': None,
                     'reason_not_going_other': 'mmm',
                     'tb_eval_comments': '',
                     'tb_eval_location': 'OTHER',
                     'tb_eval_location_other': 'mmmm',
                     'tb_diagnostic_perf': 'No',
                     'tb_diagnostics': ListModel.objects.none(),
                     'tb_diagnostics_other': None,
                     'sputum_sample': None,
                     'chest_xray': None,
                     'gene_xpert': None,
                     'tst_or_mentoux': None,
                     'covid_19': None,
                     'tb_treat_start': None,
                     'tb_prev_therapy_start': None,
                     'tb_comments': ''}

    def test_form_valid(self):

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=self.data)

        try:
            form_validator.validate()
        except ValidationError:
            self.fail('Data supplied not valid')

    def test_chest_xray_required(self):
        self.data['tb_diagnostic_perf'] = YES
        self.data['tb_diagnostics'] = ListModel.objects.filter(
            short_name='chest_xray')

        self.data['chest_xray'] = None

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('chest_xray', form_validator._errors)

    def test_gene_xpert_required(self):
        self.data['tb_diagnostic_perf'] = YES
        self.data['tb_diagnostics'] = ListModel.objects.filter(
            short_name='gene_xpert')

        self.data['gene_xpert'] = None

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('gene_xpert', form_validator._errors)

    def test_tst_or_mentoux_required(self):
        self.data['tb_diagnostic_perf'] = YES
        self.data['tb_diagnostics'] = ListModel.objects.filter(
            short_name='tst_mantoux')

        self.data['tst_or_mentoux'] = None

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tst_or_mentoux', form_validator._errors)

    def test_covid_19_required(self):
        self.data['tb_diagnostic_perf'] = YES
        self.data['tb_diagnostics'] = ListModel.objects.filter(
            short_name='covid_19_test')

        self.data['covid_19'] = None

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('covid_19', form_validator._errors)

    def test_tb_treat_start_should_be_yes(self):
        """
        tb_test_start should be No if all test results are negative
        """
        self.data['tb_diagnostic_perf'] = YES
        self.data['tb_diagnostics'] = ListModel.objects.filter(
            short_name='covid_19_test')

        self.data['covid_19'] = POS
        self.data['tb_treat_start'] = NO

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_treat_start', form_validator._errors)

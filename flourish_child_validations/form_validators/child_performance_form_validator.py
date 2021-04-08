from edc_constants.constants import OTHER
from edc_form_validators import FormValidator


class ChildPerformanceFormValidator(FormValidator):

    def clean(self):

        self.validate_other_specify(field='education_level',
                                    other_specify_field='education_level_other'
                                    )

        if self.cleaned_data.get('education_level') == 'no_schooling':
            not_required_fields = ['mathematics_marks', 'science_marks',
                                   'setswana_marks', 'english_marks',
                                   'physical_edu_marks', 'cultural_stds_marks',
                                   'social_stds_marks', 'agriculture_marks',
                                   'single_scie_marks', 'biology_marks',
                                   'chemistry_marks', 'physics_marks',
                                   'double_scie_marks']
            for field in not_required_fields:
                self.not_required_if('no_schooling', field='education_level',
                                     field_required=field)
        else:
            self.validate_other_specify(field='education_level',
                                        other_specify_field='education_level_other')
            self.required_if('pre_school', field='education_level',
                             field_required='overall_performance')

            standard1_to_standard7 = ['standard_1', 'standard_2', 'standard_3',
                                      'standard_4', 'standard_5', 'standard_6',
                                      'standard_7']
            required = ['mathematics_marks', 'science_marks', 'setswana_marks',
                        'english_marks', 'physical_edu_marks',
                        'cultural_stds_marks', 'overall_performance']

            for option in standard1_to_standard7:
                for field in required:
                    self.required_if(option, field='education_level',
                                     field_required=field, inverse=False)

            form1_to_form3 = ['form_1', 'form_2', 'form_3']

            required_field = ['mathematics_marks', 'science_marks',
                              'setswana_marks', 'english_marks',
                              'overall_performance']
            for option in form1_to_form3:
                for field in required_field:
                    self.required_if(option, field='education_level',
                                     field_required=field, inverse=False)

            required_fields = ['social_stds_marks', 'agriculture_marks']
            for option in form1_to_form3:
                for field in required_fields:
                    self.required_if(option, field='education_level',
                                     field_required=field)

            form4_to_form5 = ['form_4', 'form_5']

            field_required = ['mathematics_marks', 'setswana_marks',
                              'english_marks', 'overall_performance']
            for option in form4_to_form5:
                for field in field_required:
                    self.required_if(option, field='education_level',
                                     field_required=field, inverse=False)

            fields = ['single_scie_marks', 'biology_marks', 'chemistry_marks',
                      'physics_marks', 'double_scie_marks']
            for option in form4_to_form5:
                for field in fields:
                    self.required_if(option, field='education_level',
                                     field_required=field)

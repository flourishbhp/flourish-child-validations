from edc_constants.constants import OTHER
from edc_form_validators import FormValidator


class AcademicPerformanceFormValidator(FormValidator):

    def clean(self):
        self.commonly_required = ['mathematics_marks', 'science_marks',
                                  'setswana_marks', 'overall_performance']
        self.commonly_not_required = ['single_scie_marks', 'biology_marks',
                                      'chemistry_marks', 'physics_marks',
                                      'double_scie_marks', 'num_days']
        self.standard1_to_standard7 = ['standard_1', 'standard_2', 'standard_3',
                                       'standard_4', 'standard_5', 'standard_6',
                                       'standard_7']
        self.form1_to_form3 = ['form_1', 'form_2', 'form_3']

        super().clean()
        if self.cleaned_data.get('education_level') == 'pre_school':
            self.validate_pre_school()
        elif self.cleaned_data.get('education_level') == 'no_schooling':
            self.validate_no_schooling()
        else:
            self.validate_commonly_required_fields()
            self.validate_standard1_through_standard7()
            self.validate_form1_to_form3()
            self.validate_form4_to_form5()

            self.validate_commonly_not_required_fields()

            self.validate_other_specify(field='education_level',
                                        other_specify_field='education_level_other')

    def validate_no_schooling(self):
        not_required_fields = ['mathematics_marks', 'science_marks',
                               'setswana_marks', 'english_marks',
                               'physical_edu_marks', 'cultural_stds_marks',
                               'social_stds_marks', 'agriculture_marks',
                               'single_scie_marks', 'biology_marks',
                               'chemistry_marks', 'physics_marks',
                               'double_scie_marks', 'overall_performance',
                               'num_days']
        for field in not_required_fields:
            self.not_required_if('no_schooling', field='education_level',
                                 field_required=field)

    def validate_pre_school(self):
        self.required_if('pre_school', field='education_level',
                         field_required='overall_performance',
                         inverse=False)
        not_required_fields = (['mathematics_marks', 'science_marks',
                                'setswana_marks', 'english_marks',
                                'physical_edu_marks', 'cultural_stds_marks',
                                'social_stds_marks', 'agriculture_marks'] +
                               self.commonly_not_required)
        for field in not_required_fields:
            self.not_required_if('pre_school', field='education_level',
                                 field_required=field, inverse=False)

    def validate_standard1_through_standard7(self):
        required = ['english_marks', 'physical_edu_marks',
                    'cultural_stds_marks']
        for field in required:
            self.required_if(*self.standard1_to_standard7,
                             field='education_level',
                             field_required=field, inverse=False)
        not_required_fields = ['social_stds_marks', 'agriculture_marks']
        for field in not_required_fields:
            self.not_required_if(*self.standard1_to_standard7,
                                 field='education_level',
                                 field_required=field, inverse=False)

    def validate_form1_to_form3(self):
        required_fields = ['english_marks', 'social_stds_marks',
                           'agriculture_marks']
        for field in required_fields:
            self.required_if(*self.form1_to_form3, field='education_level',
                             field_required=field, inverse=False)
        not_required_fields = ['physical_edu_marks', 'cultural_stds_marks']
        for field in not_required_fields:
            self.not_required_if(*self.form1_to_form3, field='education_level',
                                 field_required=field, inverse=False)

    def validate_form4_to_form5(self):
        form4_to_form5 = ['form_4', 'form_5']
        field_required = ['single_scie_marks', 'biology_marks',
                          'chemistry_marks', 'physics_marks',
                          'double_scie_marks']
        for field in field_required:
            self.required_if(*form4_to_form5, field='education_level',
                             field_required=field, inverse=False)
        not_required_fields = ['english_marks', 'physical_edu_marks',
                               'cultural_stds_marks', 'social_stds_marks',
                               'agriculture_marks', 'num_days']
        for field in not_required_fields:
            self.not_required_if(*form4_to_form5, field='education_level',
                                 field_required=field, inverse=False)

    def validate_commonly_required_fields(self):
        for field in self.commonly_required:
            self.not_required_if(*[OTHER, 'no_schooling'],
                                 field='education_level', field_required=field)

    def validate_commonly_not_required_fields(self):
        for field in self.commonly_not_required:
            responses = (['no_schooling'] + self.standard1_to_standard7 +
                         self.form1_to_form3)
            self.not_required_if(*responses, field='education_level',
                                 field_required=field, inverse=False)

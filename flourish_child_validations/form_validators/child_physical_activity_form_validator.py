from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator


class ChildPhysicalActivityFormValidator(FormValidator):

    def clean(self):

        specify_hrs_mins = 'specify_hrs_mins'

        provide_hrs_min_msg = ('Please provide either hours per day or minutes'
                               ' per day')
        vig_fields_req = ['specify_vig_days', 'vig_activity_time']
        for field in vig_fields_req:
            self.required_if('days_per_week', field='vig_activity_days',
                             field_required=field)

        if self.cleaned_data.get('vig_activity_time') == specify_hrs_mins:
            if not (self.cleaned_data.get('specify_vig_time_hrs') or
                    self.cleaned_data.get('specify_vig_time_mins')):
                message = {
                        'specify_vig_time_hrs': provide_hrs_min_msg}
                self._errors.update(message)
                raise ValidationError(message)

        mod_fields_req = ['specify_mod_days', 'mod_activity_time']
        for field in mod_fields_req:
            self.required_if('days_per_week', field='mod_activity_days',
                             field_required=field)

        if self.cleaned_data.get('mod_activity_time') == specify_hrs_mins:
            if not (self.cleaned_data.get('specify_mod_time_hrs') or
                    self.cleaned_data.get('specify_mod_time_mins')):
                message = {
                    'specify_mod_time_hrs': provide_hrs_min_msg}
                self._errors.update(message)
                raise ValidationError(message)

        walking_fields_req = ['specify_walk_days', 'walking_time']
        for field in walking_fields_req:
            self.required_if('days_per_week', field='walking_days',
                             field_required=field)

        if self.cleaned_data.get('walking_time') == specify_hrs_mins:
            if not (self.cleaned_data.get('specify_walk_time_hrs') or
                    self.cleaned_data.get('specify_walk_time_mins')):
                message = {
                    'specify_walk_time_hrs': provide_hrs_min_msg}
                self._errors.update(message)
                raise ValidationError(message)

        if self.cleaned_data.get('sitting_time') == specify_hrs_mins:
            if not (self.cleaned_data.get('specify_sit_time_hrs') or
                    self.cleaned_data.get('specify_sit_time_mins')):
                message = {
                    'specify_sit_time_hrs': provide_hrs_min_msg}
                self._errors.update(message)
                raise ValidationError(message)

        vig_fields_req = ['specify_vig_days', 'mod_activity_days',
                          'walking_days', 'sitting_time']
        for field in vig_fields_req:
            self.required_if('days_per_week', field='vig_activity_days',
                             field_required=field)

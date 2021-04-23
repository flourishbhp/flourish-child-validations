from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator


class ChildPhysicalActivityFormValidator(FormValidator):

    def clean(self):

        vig_fields_req = ['specify_vig_days', 'vig_activity_time']
        for field in vig_fields_req:
            self.required_if('days_per_week', field='vig_activity_days',
                             field_required=field)

        vig_activity_time = self.cleaned_data.get('vig_activity_time')
        specify_vig_time_hrs = self.cleaned_data.get('specify_vig_time_hrs')
        specify_vig_time_mins = self.cleaned_data.get('specify_vig_time_mins')
        display_msg_at = 'specify_vig_time_hrs'

        self.time_validator(vig_activity_time, specify_vig_time_hrs,
                            specify_vig_time_mins, display_msg_at)
        self.time_validator(vig_activity_time, specify_vig_time_hrs,
                            specify_vig_time_mins, display_msg_at)

        mod_fields_req = ['specify_mod_days', 'mod_activity_time']
        for field in mod_fields_req:
            self.required_if('days_per_week', field='mod_activity_days',
                             field_required=field)

        mod_activity_time = self.cleaned_data.get('mod_activity_time')
        specify_mod_time_hrs = self.cleaned_data.get('specify_mod_time_hrs')
        specify_mod_time_mins = self.cleaned_data.get('specify_mod_time_mins')
        display_msg_at = 'specify_mod_time_hrs'

        self.time_validator(mod_activity_time, specify_mod_time_hrs,
                            specify_mod_time_mins, display_msg_at)
        self.time_validator(mod_activity_time, specify_mod_time_hrs,
                            specify_mod_time_mins, display_msg_at)

        walking_fields_req = ['specify_walk_days', 'walking_time']
        for field in walking_fields_req:
            self.required_if('days_per_week', field='walking_days',
                             field_required=field)

    def time_validator(self, time=None, hrs=None, mins=None,
                       display_msg_at=''):

        provide_hrs_min_msg = ('Please provide either hours per day or minutes'
                               ' per day')

        if time == 'specify_hrs_mins':
            hrs_to_mins = hrs * 60
            specify_mins = mins
            hrs_nd_mins = hrs_to_mins + specify_mins

            if hrs_nd_mins > 1440:
                message = {display_msg_at: 'Hours plus minutes cannot '
                                           'be more than 24 hours'}
                self._errors.update(message)
                raise ValidationError(message)

            if not hrs or mins:
                message = {display_msg_at: provide_hrs_min_msg}
                self._errors.update(message)
                raise ValidationError(message)

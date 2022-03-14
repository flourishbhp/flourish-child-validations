from edc_appointment.form_validators import AppointmentFormValidator


class ChildAppointmentFormValidator(AppointmentFormValidator):
    """
    Validates the caregiver appointment model by overriding existing appointment
    validation functions.
    """

    def validate_appt_new_or_complete(self):
        pass

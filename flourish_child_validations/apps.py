from django.apps import AppConfig as DjangoAppconfig
from edc_appointment.appointment_config import AppointmentConfig
from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
from edc_appointment.constants import COMPLETE_APPT
from edc_timepoint import Timepoint, TimepointCollection
# from edc_visit_tracking.apps import (
# AppConfig as BaseEdcVisitTrackingAppConfig)
from edc_timepoint.apps import AppConfig as BaseEdcTimepointAppConfig


class AppConfig(DjangoAppconfig):
    name = 'flourish_child_validations'
    verbose_name = 'Flourish Child Form Validations'


#
# class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
# visit_models = {
# 'flourish_child': ('child_visit', 'flourish_child.childvisit')}

class EdcTimepointAppConfig(BaseEdcTimepointAppConfig):
    timepoints = TimepointCollection(
        timepoints=[
            Timepoint(
                model='flourish_child_validations.appointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
        ])


class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
    configurations = [
        AppointmentConfig(
            model='flourish_child_validations.appointment',
            related_visit_model='flourish_caregiver.childvisit',
            appt_type='clinic'),
    ]

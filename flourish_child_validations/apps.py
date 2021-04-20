from django.apps import AppConfig as DjangoAppconfig
# from edc_visit_tracking.apps import (
    # AppConfig as BaseEdcVisitTrackingAppConfig)


class AppConfig(DjangoAppconfig):
    name = 'flourish_child_validations'
    verbose_name = 'Flourish Child Form Validations'

#
# class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
    # visit_models = {
        # 'flourish_child': ('child_visit', 'flourish_child.childvisit')}

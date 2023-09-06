from django.apps import apps as django_apps


def caregiver_subject_identifier(subject_identifier, registered_subject_cls=None):
    registered_subject_cls = registered_subject_cls or django_apps.get_model(
        'edc_registration.registeredsubject')
    try:
        registered_subject = registered_subject_cls.objects.get(
                subject_identifier=subject_identifier)
    except registered_subject_cls.DoesNotExist:
        return None
    else:
        return registered_subject.relative_identifier

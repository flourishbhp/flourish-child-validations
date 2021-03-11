from django.conf import settings

if settings.APP_NAME == 'flourish_child_validations':
    from .tests import models

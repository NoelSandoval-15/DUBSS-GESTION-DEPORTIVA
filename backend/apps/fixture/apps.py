from django.apps import AppConfig
class FixtureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.fixture"
    label = "fixture"
    verbose_name = "Fixture"

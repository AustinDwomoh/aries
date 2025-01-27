from django.apps import AppConfig


class ClubsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clubs'

    def ready(self):
        """imports club signals"""
        import clubs.signals  
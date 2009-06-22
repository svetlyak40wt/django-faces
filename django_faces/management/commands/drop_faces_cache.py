from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Drop cache django-faces's avatars cache."
    requires_model_validation = True

    def handle_noargs(self, **options):
        from django_faces.models import CacheState
        CacheState.objects.all().delete()


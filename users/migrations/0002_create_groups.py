from django.db import migrations
from django.contrib.auth.models import Group

def create_groups(apps, schema_editor):
    Group.objects.get_or_create(name='analyst')
    Group.objects.get_or_create(name='viewer')

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # ajusta si tu última migración tiene otro nombre
    ]
    operations = [
        migrations.RunPython(create_groups),
    ]
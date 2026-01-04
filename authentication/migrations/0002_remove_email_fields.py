# Generated migration to remove email verification fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_email_verified',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='status',
        ),
    ]

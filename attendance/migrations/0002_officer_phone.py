# Generated by Django 3.0.2 on 2020-01-12 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='phone',
            field=models.CharField(max_length=10, null=True),
        ),
    ]

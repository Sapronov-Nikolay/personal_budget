# Generated by Django 5.2 on 2025-05-03 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_budget', '0006_recalculate_summaries'),
    ]

    operations = [
        migrations.AddField(
            model_name='summary',
            name='initial_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]

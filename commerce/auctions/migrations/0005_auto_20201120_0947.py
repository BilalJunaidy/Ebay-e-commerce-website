# Generated by Django 3.1.3 on 2020-11-20 14:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='bid_amount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-01 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailoring', '0003_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='asa_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='escrow_address',
            field=models.CharField(blank=True, max_length=58, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='is_released',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]

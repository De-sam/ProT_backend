# Generated by Django 5.1.2 on 2024-11-01 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0005_customuser_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='wallet_address',
            field=models.CharField(blank=True, help_text='Algorand wallet address for transactions.', max_length=58, null=True),
        ),
    ]
# Generated by Django 5.1.2 on 2024-10-31 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0002_alter_customuser_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='customer_id',
            field=models.CharField(blank=True, help_text='Unique identifier for customers, 6 characters.', max_length=6, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('TAILOR', 'Tailor'), ('CUSTOMER', 'Customer')], default='CUSTOMER', help_text='Role of the user, either Tailor or Customer.', max_length=10),
        ),
    ]

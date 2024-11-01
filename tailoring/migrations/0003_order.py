# Generated by Django 5.1.2 on 2024-11-01 13:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailoring', '0002_design_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_id', models.CharField(blank=True, max_length=64, null=True)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed')], default='PENDING', max_length=10)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('design', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='tailoring.design')),
            ],
        ),
    ]
# Generated by Django 5.1.3 on 2024-12-12 20:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_mouvment_is_stock'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'permissions': [('view_dashboard', 'Can view dashboard')]},
        ),
    ]

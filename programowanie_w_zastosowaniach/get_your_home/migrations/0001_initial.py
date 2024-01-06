# Generated by Django 5.0 on 2024-01-06 15:14

import django.db.models.deletion
import get_your_home.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
            options={
                'verbose_name': 'Zdjęcie',
                'verbose_name_plural': 'Zdjęcia',
            },
        ),
        migrations.CreateModel(
            name='SaleAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('studio', 'Mieszkanie jednopokojowe (kawalerka)'), ('m2', 'Mieszkanie dwupokojowe'), ('m3', 'Mieszkanie trzypokojowe'), ('m4', 'Mieszkanie czteropokojowe'), ('apartment', 'Apartament'), ('loft', 'Loft'), ('single_family_house', 'Dom jednorodzinny'), ('apartment_building', 'Mieszkanie w bloku mieszkalnym'), ('tenement_house', 'Mieszkanie w kamienicy'), ('townhouse', 'Dom szeregowy'), ('dormitory', 'Mieszkanie w akademiku (dla studentów)')], max_length=19)),
                ('status', models.CharField(choices=[('canceled', 'Anulowane'), ('sold', 'Sprzedane'), ('blocked', 'Zablokowane'), ('purchase', 'Do kupienia'), ('rental', 'Do wynajęcia'), ('long_term_lease', 'Wynajem długoterminowy'), ('short_term_lease', 'Wynajem krótkoterminowy'), ('co_ownership', 'Współwłasność'), ('tenancy', 'Dzierżawa'), ('commercial_property', 'Nieruchomość komercyjna')], max_length=19)),
                ('heating_type', models.CharField(choices=[('unknown', 'Nie podany'), ('gas', 'Ogrzewanie gazowe'), ('electric', 'Ogrzewanie elektryczne'), ('oil', 'Ogrzewanie olejowe'), ('biomass', 'Ogrzewanie na biomasę'), ('underfloor_water', 'Ogrzewanie podłogowe wodne'), ('solar', 'Ogrzewanie słoneczne'), ('heat_pump', 'Pompy ciepła'), ('steam', 'Ogrzewanie parowe'), ('hot_water', 'Ogrzewanie wodne'), ('fireplace', 'Ogrzewanie kominowe')], default='unknown', max_length=16, null=True)),
                ('area', models.DecimalField(decimal_places=2, max_digits=10)),
                ('address_city', models.CharField(max_length=50)),
                ('address_street', models.CharField(max_length=150)),
                ('address_post_code', models.CharField(max_length=6, null=True, validators=[get_your_home.models.post_code_validator])),
                ('address_number', models.CharField(max_length=20)),
                ('number_of_rooms', models.SmallIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=100000)),
                ('description', models.CharField(max_length=5000, null=True)),
                ('build_year', models.SmallIntegerField(null=True)),
                ('admin_note', models.CharField(max_length=5000, null=True)),
                ('publication_date', models.DateField()),
                ('owner_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('photos', models.ManyToManyField(to='get_your_home.photo')),
            ],
            options={
                'verbose_name': 'Ogłoszenie',
                'verbose_name_plural': 'Ogłoszenia',
            },
        ),
    ]

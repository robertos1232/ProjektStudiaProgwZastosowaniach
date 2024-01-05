from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy

# TODO: Dodać polskie tłumaczenia
def post_code_validator(value: str):
    if len(value) != 6:
        raise ValidationError(
            gettext_lazy("%(value)s must contains exactly 6 characters"),
            params={"value": value},
        )
    if value[2] != '-':
        raise ValidationError(
            gettext_lazy("%(value)s must contains '-' at 3rd character"),
            params={"value": value},
        )
    for char in value[0:3:6]:
        try:
            int(char)
        except ValueError:
            raise ValidationError(
                gettext_lazy("Invalid character '%(char)s' in given post code - each character must be a number"),
                params={"char": char},
            )


class Photo(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Zdjęcie'
        verbose_name_plural = 'Zdjęcia'


class SaleAnnouncement(models.Model):
    HEATING_TYPES = {
        "unknown": "Nie podany",
        "gas": "Ogrzewanie gazowe",
        "electric": "Ogrzewanie elektryczne",
        "oil": "Ogrzewanie olejowe",
        "biomass": "Ogrzewanie na biomasę",
        "underfloor_water": "Ogrzewanie podłogowe wodne",
        "solar": "Ogrzewanie słoneczne",
        "heat_pump": "Pompy ciepła",
        "steam": "Ogrzewanie parowe",
        "hot_water": "Ogrzewanie wodne",
        "fireplace": "Ogrzewanie kominowe"
    }

    PROPERTY_TYPES = {
        "studio": "Mieszkanie jednopokojowe (kawalerka)",
        "m2": "Mieszkanie dwupokojowe",
        "m3": "Mieszkanie trzypokojowe",
        "m4": "Mieszkanie czteropokojowe",
        "apartment": "Apartament",
        "loft": "Loft",
        "single_family_house": "Dom jednorodzinny",
        "apartment_building": "Mieszkanie w bloku mieszkalnym",
        "tenement_house": "Mieszkanie w kamienicy",
        "townhouse": "Dom szeregowy",
        "dormitory": "Mieszkanie w akademiku (dla studentów)"
    }

    STATUSES = {
        "canceled": "Anulowane",
        "sold": "Sprzedane",
        "blocked": "Zablokowane",
        "purchase": "Do kupienia",
        "rental": "Do wynajęcia",
        "long_term_lease": "Wynajem długoterminowy",
        "short_term_lease": "Wynajem krótkoterminowy",
        "co_ownership": "Współwłasność",
        "tenancy": "Dzierżawa",
        "commercial_property": "Nieruchomość komercyjna",
    }

    type = models.CharField(
        choices=PROPERTY_TYPES,
        max_length=len(max(PROPERTY_TYPES, key=len)),
    )
    status = models.CharField(
        choices=STATUSES,
        max_length=len(max(STATUSES, key=len)),
    )
    heating_type = models.CharField(
        choices=HEATING_TYPES,
        max_length=len(max(HEATING_TYPES, key=len)),
        default="unknown",
        null=True
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    address_city = models.CharField(
        max_length=50
    )
    address_street = models.CharField(
        max_length=150
    )
    address_post_code = models.CharField(
        max_length=6,
        validators=[post_code_validator],
    )
    address_number = models.CharField(
        max_length=20
    )
    number_of_rooms = models.SmallIntegerField()
    price = models.DecimalField(
        max_digits=100000,
        decimal_places=2,
        null=False
    )
    description = models.CharField(
        max_length=5000,
        null=True
    )
    build_year = models.SmallIntegerField(
        null=True
    )
    owner_user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
    )

    photos = models.ManyToManyField(
        Photo
    )

    def __str__(self):
        return (
            f'{self.address_city} - {self.address_street} {self.address_number} - {self.address_post_code} / '
            f'{self.STATUSES.get(str(self.status))}'
        )

    class Meta:
        verbose_name = 'Ogłoszenie'
        verbose_name_plural = 'Ogłoszenia'

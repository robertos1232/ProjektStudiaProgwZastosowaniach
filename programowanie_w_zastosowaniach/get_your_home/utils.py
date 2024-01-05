import uuid

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.http import QueryDict

from .models import SaleAnnouncement, Photo


def get_context_to_filter(with_nulls=False, statuses_to_skip=None):
    if statuses_to_skip is None:
        statuses_to_skip = []

    all_data = {
        "all": "Wszystkie"
    }
    ann_types = SaleAnnouncement.PROPERTY_TYPES
    statutes = {k: v for k, v in SaleAnnouncement.STATUSES.items() if k not in statuses_to_skip}
    heating_types = {k: v for k, v in SaleAnnouncement.STATUSES.items() if k not in statuses_to_skip}
    if with_nulls:
        ann_types = all_data | ann_types
        statutes = all_data | statutes
        heating_types = all_data | heating_types

    return {
        "ann_types": ann_types,
        "statutes": statutes,
        "heating_types": heating_types,
    }


def check_fields(request_data: QueryDict, required_fields: dict[str, str]) -> str:
    for english_field, polish_field in required_fields.items():
        if not request_data.get(english_field):
            return f'Brakuje pola {polish_field}, następujące pola są wymagane: {", ".join(required_fields.values())}'
    return ''


def save_photo(announcement: SaleAnnouncement, photo: TemporaryUploadedFile):
    photo_base_path = (
        f"{announcement.address_city}_"
        f"{announcement.address_street}_"
        f"{announcement.address_number}"
    )

    if not photo.content_type.startswith('image'):
        return None
    photo_format = photo.content_type.split('/')[1]
    new_photo = Photo(
        name=f'{photo_base_path}_{str(uuid.uuid4())}.{photo_format}'
    )

    with open(f'{settings.MEDIA_ROOT}/{new_photo.name}', 'wb') as photo_file:
        photo_file.writelines(photo.readlines())
    new_photo.save()
    return new_photo

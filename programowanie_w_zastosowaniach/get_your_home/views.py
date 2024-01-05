import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.http import HttpResponseRedirect, QueryDict, Http404
from django.shortcuts import render, redirect
from .models import SaleAnnouncement, Photo
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

_skip_statutes = ["canceled", "sold", "blocked"]


def get_context_to_filter(with_nulls=False):
    all_data = {
        "all": "Wszystkie"
    }
    ann_types = SaleAnnouncement.PROPERTY_TYPES
    statutes = {k: v for k, v in SaleAnnouncement.STATUSES.items() if k not in _skip_statutes}
    heating_types = {k: v for k, v in SaleAnnouncement.STATUSES.items() if k not in _skip_statutes}
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


# This view is used as index
def list_of_sale_announcement(request):
    announcements = SaleAnnouncement.objects.all().exclude(
        status__in=_skip_statutes,
    )

    context = get_context_to_filter(True)

    if request.GET:
        req = request.GET
        to_sort_base = {
            "type": req.get('typeOfAnn', 'all'),
            "status": req.get('typeOfStatus', 'all'),
            "heating_type": req.get('typeOfHeating', 'all'),
            "area__gte": req.get('minArea', '-1'),
            "area__lte": req.get('maxArea', '-1'),
            "city": req.get("city", "all"),
            "street": req.get("city", "all"),
            "number_of_rooms__gte": req.get('minRoomsNumber', '-1'),
            "number_of_rooms__lte": req.get('maxRoomsNumber', '-1'),
        }
        to_sort = {
            k: v for k, v in to_sort_base.items() if v not in ['-1', 'all', '']
        }
        announcements = announcements.filter(**to_sort)

    context.update({
        "announcements": {
            announcement: announcements.get().photos.get() for announcement in announcements
        }
    })

    return render(
        request=request,
        template_name="index.html",
        context=context,
    )


# TODO: Save state
def login_view(request):
    template_name_to_use = 'account/login.html'
    if request.method == "POST":
        error_message = check_fields(request.POST, {
            "username": "nazwa użytkownika",
            "password": "hasło"
        })
        username = request.POST.get("username", '')
        password = request.POST.get("password", '')
        if error_message:
            return render(
                request=request,
                template_name=template_name_to_use,
                context={
                    "warning": error_message
                }
            )
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect("/")

        return render(
            request=request,
            template_name=template_name_to_use,
            context={
                "warning": "Email lub hasło, jest błędne, spróbuj ponownie"
            }
        )

    return render(
        request=request,
        template_name=template_name_to_use,
        context={}
    )


# TODO: Save state
def register_view(request):
    template_name_to_use = 'account/register.html'

    if request.method == "POST":
        error_message = check_fields(request.POST, {
            "username": "nazwa użytkownika",
            "password": "hasło",
            "email": "email"
        })
        if error_message:
            return render(
                request=request,
                template_name=template_name_to_use,
                context={
                    "warning": error_message
                }
            )

        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        users = User.objects.filter(username=username) | User.objects.filter(email=email)
        if users:
            return render(
                request=request,
                template_name=template_name_to_use,
                context={
                    "warning": "Konto o takiej nazwe użytkownika, lub emailem istnieje"
                }
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        user.first_name = request.POST.get("firstName", "")
        user.last_name = request.POST.get("lastName", "")
        user.save()
        login(request, user)
        return HttpResponseRedirect("/")

    return render(
        request=request,
        template_name=template_name_to_use,
        context={}
    )


@login_required(login_url="/login/")
def profile_view(request):
    announcements = SaleAnnouncement.objects.all().filter(
        owner_user__email__regex=request.user.email
    )
    return render(
        request=request,
        template_name="account/profile.html",
        context={
            "announcements": announcements,
        }
    )


def details(request, city, street, number):
    announcement = SaleAnnouncement.objects.get(
        address_city=city,
        address_street=street,
        address_number=number,
    )

    if not announcement:
        raise Http404()

    photos = announcement.photos.all()

    context = {
        "ann": announcement,
        "photos": photos
    }

    return render(
        request=request,
        template_name="details.html",
        context=context
    )


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


@login_required(login_url="/login/")
def add_announcement(request):
    if request.POST:
        new_announcement = SaleAnnouncement(
            type=request.POST.get('typeOfAnn'),
            price=int(request.POST.get('price')),
            status=request.POST.get('typeOfStatus'),
            heating_type=request.POST.get('heating_type'),
            area=request.POST.get('area'),
            address_city=request.POST.get('city'),
            address_street=request.POST.get('street'),
            address_number=request.POST.get('addressNumber'),
            address_post_code=request.POST.get('postCode', ''),
            number_of_rooms=int(request.POST.get('roomsNumber')) if request.POST.get('roomsNumber') != "" else 0,
            description=request.POST.get('description', ''),
            build_year=int(request.POST.get('buildYear', 0)),
            owner_user_id=request.user.id
        )

        photo = request.FILES.get('photo', '')
        new_announcement.save()

        if photo:
            new_photo = save_photo(new_announcement, photo)
            new_announcement.photos.add(new_photo)
            new_announcement.save()

        return redirect(
            details.__name__,
            city=new_announcement.address_city,
            street=new_announcement.address_street,
            number=new_announcement.address_number
        )

    return render(
        request=request,
        template_name="add_announcement.html",
        context=get_context_to_filter()
    )

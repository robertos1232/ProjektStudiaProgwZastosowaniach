import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from .models import SaleAnnouncement
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .utils import get_context_to_filter, check_fields, save_photo, validate_add_edit_ann_request, \
    get_required_fields_and_num_fields_for_announcement, delete_photo

_skip_statutes = ["canceled", "sold", "blocked"]


# This view is used as index
def list_of_sale_announcement(request):
    announcements = SaleAnnouncement.objects.all().exclude(
        status__in=_skip_statutes,
    )

    context = get_context_to_filter(True, _skip_statutes)

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
            announcement: announcement.photos.first() for announcement in announcements
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
            "announcements": {
                announcement: announcement.photos.first() for announcement in announcements
            }
        }
    )


def details(request, publication_date, city, street, number):
    announcement = SaleAnnouncement.objects.get(
        address_city=city,
        address_street=street,
        address_number=number,
        publication_date=publication_date
    )

    if not announcement:
        raise Http404()

    photos = announcement.photos.all()

    context = {
        "ann": announcement,
        "photos": photos,
        "owner": announcement.owner_user.id == request.user.id
    }

    return render(
        request=request,
        template_name="details.html",
        context=context
    )


@login_required(login_url="/login/")
def add_announcement(request):
    base_context = get_context_to_filter(statuses_to_skip=_skip_statutes)
    template_to_use = "announcement/add_edit_announcement.html"
    if request.POST:
        # Walidacja wymaganych pól
        error_message = validate_add_edit_ann_request(
            request.POST,
            *get_required_fields_and_num_fields_for_announcement()
        )
        if error_message:
            context = {
                'warning': error_message
            } | base_context
            return render(request, template_to_use, context)

        # Tworzenie nowego ogłoszenia
        new_announcement = SaleAnnouncement(
            type=request.POST.get('typeOfAnn'),
            price=request.POST.get('price'),
            status=request.POST.get('typeOfStatus'),
            heating_type=request.POST.get('heating_type'),
            area=request.POST.get('area'),
            address_city=request.POST.get('city'),
            address_street=request.POST.get('street'),
            address_number=request.POST.get('addressNumber'),
            address_post_code=request.POST.get('postCode', ''),
            number_of_rooms=request.POST.get('roomsNumber'),
            description=request.POST.get('description', ''),
            build_year=request.POST.get('buildYear'),
            owner_user_id=request.user.id,
            publication_date=datetime.date.today(),
        )

        photo = request.FILES.get('photo', '')
        if not photo:
            context = {
                "warning": "Zdjęcie jest wymagane."
            } | get_context_to_filter()
            return render(
                request=request,
                template_name=template_to_use,
                context=context
            )

        if SaleAnnouncement.objects.exclude(
            status__in=_skip_statutes
        ).filter(
            address_city=new_announcement.address_city,
            address_street=new_announcement.address_street,
            address_number=new_announcement.address_number,
        ).first():
            context = {
                "warning": "Istnieje już aktywne ogłoszenie z takim adresem."
            } | get_context_to_filter()
            return render(
                request=request,
                template_name=template_to_use,
                context=context
            )

        new_announcement.save()
        new_photo = save_photo(new_announcement, photo)
        new_announcement.photos.add(new_photo)
        new_announcement.save()

        return redirect(
            details.__name__,
            publication_date=new_announcement.publication_date,
            city=new_announcement.address_city,
            street=new_announcement.address_street,
            number=new_announcement.address_number
        )

    return render(
        request=request,
        template_name=template_to_use,
        context=base_context
    )


@login_required(login_url="/login/")
def password_change(request):
    template_name_to_use = 'account/password_change.html'
    if request.POST:
        error_message = check_fields(request.POST, {
            "password": "hasło"
        })

        if error_message:
            return render(
                request=request,
                template_name=template_name_to_use,
                context={"warning": error_message}
            )

        user = request.user
        user.set_password(request.POST.get("password"))
        user.save()
        request.session['info'] = "hasło zostało zaktualizowane"
        login(request, user)

        return redirect(
            profile_view.__name__
        )

    return render(
        request=request,
        template_name=template_name_to_use,
        context={}
    )


@login_required(login_url="/login/")
def change_user_data(request):
    template_name_to_use = 'account/change_user_data.html'
    if request.POST:
        u = request.user
        email = request.POST.get("email")
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")

        if email:
            u.email = email
        if first_name:
            u.first_name = first_name
        if last_name:
            u.last_name = last_name

        u.save()
        login(request, u)
        return redirect(
            profile_view.__name__
        )

    return render(
        request=request,
        template_name=template_name_to_use,
        context={}
    )


@login_required(login_url='/login/')
def admin_adit_ann(request, publication_date, city, street, number):
    template_name_to_use = "announcement/admin_edit.html"

    if not request.user.is_superuser:
        return Http404()

    announcement = SaleAnnouncement.objects.get(
        address_city=city,
        address_street=street,
        address_number=number,
        publication_date=publication_date,
    )

    if not announcement:
        return Http404()

    if request.POST:
        if request.POST.get("blocked", '') == "blocked":
            announcement.status = "blocked"

        announcement.admin_note = request.POST.get("comment", "")
        announcement.save()

    return render(
        request=request,
        template_name=template_name_to_use,
        context={
            "blocked": announcement.status == "blocked",
            "comment": announcement.admin_note
        }
    )


@login_required(login_url='/login/')
def edit_announcement(request, publication_date, city, street, number):
    template_name_to_use = "announcement/add_edit_announcement.html"

    announcement = SaleAnnouncement.objects.get(
        address_city=city,
        address_street=street,
        address_number=number,
        publication_date=publication_date,
    )

    if not announcement.owner_user.id == request.user.id or not announcement:
        return Http404()

    base_context = get_context_to_filter(statuses_to_skip=["blocked"]) | {
        "ann": announcement
    }

    if request.POST:
        # Walidacja wymaganych pól
        error_message = validate_add_edit_ann_request(
            request.POST,
            *get_required_fields_and_num_fields_for_announcement()
        )
        if error_message:
            context = {
                'warning': error_message
            } | base_context
            return render(request, template_name_to_use, context)

        announcement.type = request.POST.get('typeOfAnn')
        announcement.price = request.POST.get('price')
        announcement.status = request.POST.get('typeOfStatus')
        announcement.heating_type = request.POST.get('heating_type')
        announcement.area = request.POST.get('area')
        announcement.address_city = request.POST.get('city')
        announcement.address_street = request.POST.get('street')
        announcement.address_number = request.POST.get('addressNumber')
        announcement.address_post_code = request.POST.get('postCode', '')
        announcement.number_of_rooms = request.POST.get('roomsNumber')
        announcement.description = request.POST.get('description', '')
        announcement.build_year = request.POST.get('buildYear')
        announcement.publication_date = announcement.publication_date
        announcement.save()
        photo = request.FILES.get('photo', '')
        if photo:
            new_photo = save_photo(announcement, photo)
            if new_photo:
                announcement.photos.add(new_photo)
                announcement.save()
                delete_photo(announcement)

        return redirect(
            details.__name__,
            publication_date=announcement.publication_date,
            city=announcement.address_city,
            street=announcement.address_street,
            number=announcement.address_number
        )

    return render(
        request=request,
        template_name=template_name_to_use,
        context=base_context
    )
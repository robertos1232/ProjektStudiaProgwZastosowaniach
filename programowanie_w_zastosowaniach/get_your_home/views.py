from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from .models import SaleAnnouncement
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .utils import get_context_to_filter, check_fields, save_photo

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


@login_required(login_url="/login/")
def add_announcement(request):
    base_context = get_context_to_filter(statuses_to_skip=_skip_statutes)
    if request.POST:
        # Walidacja wymaganych pól
        required_fields = {
            'typeOfAnn': 'Typ ogłoszenia',
            'typeOfStatus': 'Status ogłoszenia',
            'typeOfHeating': 'Typ ogrzewania',
            'price': 'Cena',
            'buildYear': 'Rok budowy',
            'area': 'Powierzchnia',
            'city': 'Miasto',
            'street': 'Ulica',
            'addressNumber': 'Numer domu/mieszkania',
        }

        error_message = check_fields(request.POST, required_fields)
        if error_message:
            context = {
                'warning': error_message
            } | base_context
            return render(request, "add_announcement.html", context)

        # Konwersja i dodatkowa walidacja dla pól liczbowych
        try:
            price = int(request.POST.get('price'))
            number_of_rooms = int(request.POST.get('roomsNumber')) if request.POST.get('roomsNumber') else 0
            build_year = int(request.POST.get('buildYear', 0))
        except ValueError as e:
            context = {
                'warning': e
            } | base_context
            return render(request, "add_announcement.html", context)

        # Tworzenie nowego ogłoszenia
        new_announcement = SaleAnnouncement(
            type=request.POST.get('typeOfAnn'),
            price=price,
            status=request.POST.get('typeOfStatus'),
            heating_type=request.POST.get('heating_type'),
            area=request.POST.get('area'),
            address_city=request.POST.get('city'),
            address_street=request.POST.get('street'),
            address_number=request.POST.get('addressNumber'),
            address_post_code=request.POST.get('postCode', ''),
            number_of_rooms=number_of_rooms,
            description=request.POST.get('description', ''),
            build_year=build_year,
            owner_user_id=request.user.id
        )

        photo = request.FILES.get('photo', '')
        new_announcement.save()
        if not photo:
            context = {
                "warning": "Zdjęcie jest wymagane."
            } | get_context_to_filter()
            return render(
                request=request,
                template_name="add_announcement.html",
                context=context
            )

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

from django.urls import path

from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.list_of_sale_announcement, name='index'),
    path("login/", views.login_view, name='login_form'),
    path("register/", views.register_view, name='register_form'),
    path('logout/', LogoutView.as_view(next_page=""), name='logout'),
    path("profile/", views.profile_view, name='profile_view'),
    path("add/", views.add_announcement, name='add_new_announcement'),
    path("view/<city>/<street>/<number>/", views.details, name="details"),
    path("filter/", views.list_of_sale_announcement, name="filtered_list"),
]
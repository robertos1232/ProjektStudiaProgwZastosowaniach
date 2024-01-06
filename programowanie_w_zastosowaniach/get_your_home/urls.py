from datetime import datetime

from django.urls import path, register_converter

from . import views
from django.contrib.auth.views import LogoutView


class DateConverter:
    regex = r'\d{4}-\d{1,2}-\d{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, self.format).date()

    def to_url(self, value):
        return value.strftime(self.format)


register_converter(DateConverter, 'date')

urlpatterns = [
    path("", views.list_of_sale_announcement, name='index'),
    path("login/", views.login_view, name='login_form'),
    path("register/", views.register_view, name='register_form'),
    path('logout/', LogoutView.as_view(next_page=""), name='logout'),
    path("profile/", views.profile_view, name='profile_view'),
    path("add/", views.add_announcement, name='add_new_announcement'),
    path("view/<date:publication_date>/<city>/<street>/<number>/", views.details, name="details"),
    path("view/<date:publication_date>/<city>/<street>/<number>/admin", views.admin_adit_ann, name="admin_edit"),
    path("view/<date:publication_date>/<city>/<street>/<number>/edit", views.edit_announcement, name="edit_ann"),
    path("filter/", views.list_of_sale_announcement, name="filtered_list"),
    path("profile/password_change/", views.password_change, name="password_change"),
    path("profile/user_data_change/", views.change_user_data, name="user_data_change"),
]

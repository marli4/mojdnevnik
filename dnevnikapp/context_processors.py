from django.urls import reverse
from datetime import date
from django.utils import timezone
from .converters import DateConverter

def header_context(request):
    user = request.user
    links = []

    if not user.is_authenticated:
        links = [
            {"title":"Вход", "url":reverse("login")},
        ]
    elif user.role == "admin":
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Группы", "url":reverse("groups")},
            {"title":"Профиль", "url":reverse("profile")},
        ]

    elif user.role == "student":
        today = timezone.localdate()
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Дневник", "url":diary_url},
            {"title":"Журнал", "url":reverse("gradebook", kwargs={"groupid":request.user.group_id})},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    elif user.role == "parent":
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Дети", "url":reverse("children")},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    elif user.role == "teacher":
        today = timezone.localdate()
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Занятия", "url":reverse("lessons", kwargs={"date": today})},
            {"title":"Группы", "url":reverse("groups")},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    return {"headerlinks":links}
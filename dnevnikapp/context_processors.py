from django.urls import reverse
from datetime import date
from django.utils import timezone
from .converters import DateConverter

def header_context(request):
    user = request.user
    links = []
    today = timezone.localdate()
    if not user.is_authenticated:
        links = [
            {"title":"Вход", "url":reverse("login")},
        ]
    elif user.role == "admin":
        links = [
            {"title":"Главная", "url":reverse("home")},
            {"title":"Группы", "url":reverse("groups")},
            {"title":"Профиль", "url":reverse("profile")},
        ]

    elif user.role == "student":
        links = [
            {"title":"Главная", "url":reverse("home")},
            {"title":"Дневник", "url":reverse("diary", kwargs={"date": today})},
            {"title":"Журнал", "url":reverse("gradebook", kwargs={"groupid":request.user.group_id})},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    elif user.role == "parent":
        links = [
            {"title":"Главная", "url":reverse("home")},
            {"title":"Дети", "url":reverse("children")},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    elif user.role == "teacher":
        today = timezone.localdate()
        links = [
            {"title":"Главная", "url":reverse("home")},
            {"title":"Занятия", "url":reverse("lessons", kwargs={"date": today})},
            {"title":"Группы", "url":reverse("groups")},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    return {"headerlinks":links, "today":today}
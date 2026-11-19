from django.urls import reverse
from datetime import date
from django.utils import timezone
from .converters import DateConverter

def header_context(request):
    user = request.user

    if not user.is_authenticated:
        links = [
            {"title":"Вход", "url":reverse("login")},
        ]
    elif user.role == "admin":
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Группы", "url":reverse("profile")},
            {"title":"Профиль", "url":reverse("profile")},
        ]

    elif user.role == "student":
        today = timezone.localdate()
        diary_url = reverse("diary", kwargs={"date": today})
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Дневник", "url":diary_url},
            {"title":"Журнал", "url":reverse("profile")},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    elif user.role == "parent":
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Дети", "url":reverse("profile")},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    elif user.role == "teacher":
        links = [
            {"title":"Главная", "url":reverse("profile")},
            {"title":"Занятия", "url":reverse("profile")},
            {"title":"Группы", "url":reverse("profile")},
            {"title":"Профиль", "url":reverse("profile")},
        ]
    return {"headerlinks":links}
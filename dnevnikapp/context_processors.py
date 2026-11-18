from django.urls import reverse

def header_context(request):
    user = request.user

    if not user.is_authenticated:
        links = [
            {"title":"Вход", "url":reverse("login")},
        ]
    elif user.role == "admin":
        links = [
            {"title":"Главная", "url":"profile"},
            {"title":"Группы", "url":"profile"},
            {"title":"Профиль", "url":"profile"},
        ]

    elif user.role == "student":
        links = [
            {"title":"Главная", "url":"profile"},
            {"title":"Дневник", "url":"profile"},
            {"title":"Журнал", "url":"profile"},
            {"title":"Профиль", "url":"profile"},
        ]
    elif user.role == "parent":
        links = [
            {"title":"Главная", "url":"profile"},
            {"title":"Дети", "url":"profile"},
            {"title":"Профиль", "url":"profile"},
        ]
    elif user.role == "teacher":
        links = [
            {"title":"Главная", "url":"profile"},
            {"title":"Занятия", "url":"profile"},
            {"title":"Группы", "url":"profile"},
            {"title":"Профиль", "url":"profile"},
        ]
    return {"headerlinks":links}
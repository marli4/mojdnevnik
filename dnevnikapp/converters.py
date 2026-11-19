from datetime import date

class DateConverter:
    regex = r"[0-9]{2}-[0-9]{2}-[0-9]{4}"
    def to_python(self, value: str) -> date:
        return date.strptime(value, "%d-%m-%Y")
    def to_url(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
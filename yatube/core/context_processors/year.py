import datetime


def year(request):
    year_footer = datetime.date.today()
    """Добавляет переменную с текущим годом."""
    return {
        'year': int(year_footer.year),
    }

from django import template

register = template.Library()


@register.filter
def icon(obj):
    icons = {
        "bookings": "book",
        "customer ads": "address-card",
        "driver ads": "id-card",
        "customers": "user",
        "drivers": "user-secret",
        "users": "users",
        "vehicle categories": "table",
        "vehicles": "bus",
    }
    name = obj["name"].lower()
    return icons[name]

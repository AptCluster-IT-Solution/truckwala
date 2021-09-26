from itertools import chain

from django.db.models import Q, F, Prefetch
from django.db.models import CharField, Value

from users.models import User


def dashboard(request):
    if (
        request.path == "/"
        and request.user.is_authenticated
        and request.user.is_superuser
    ):
        driver_users = (
            User.objects.prefetch_related(Prefetch("driver_profile", to_attr="profile"))
            .filter(
                driver_profile__isnull=False, driver_profile__is_verified__isnull=True
            )
            .distinct()
            .annotate(user_type=Value("d", output_field=CharField()))
        )

        customer_users = (
            User.objects.prefetch_related(
                Prefetch("customer_profile", to_attr="profile")
            )
            .filter(
                customer_profile__isnull=False,
                customer_profile__is_verified__isnull=True,
            )
            .distinct()
            .annotate(user_type=Value("c", output_field=CharField()))
        )

        users = sorted(
            chain(driver_users, customer_users),
            key=lambda instance: instance.driver_profile.created
            if hasattr(instance, "driver_profile")
            else instance.customer_profile.created,
        )

        for user in users:
            for doc in user.profile.documents.all():
                print(doc.image.url)

        return {"users": users}
    return {}

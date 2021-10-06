from django.contrib import admin

from bookings.models import CustomerAd, DriverAd, Booking, CustomerAdBid, DriverAdBid, Transaction

admin.site.register(CustomerAdBid)
admin.site.register(DriverAdBid)
admin.site.register(Transaction)
admin.site.register(CustomerAd)
admin.site.register(DriverAd)
admin.site.register(Booking)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Movie, Hall, Session, Ticket, Discount

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'birth_date')}),
    )

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'director', 'release_date', 'age_rating')
    list_filter = ('genre', 'age_rating')
    search_fields = ('title', 'director')

class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'seats_rows', 'seats_per_row', 'total_seats')
    
    def total_seats(self, obj):
        return obj.total_seats
    total_seats.short_description = 'Всего мест'

class SessionAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'start_time', 'end_time', 'base_price')
    list_filter = ('hall', 'start_time')
    search_fields = ('movie__title',)
    date_hierarchy = 'start_time'

class TicketAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'row', 'seat', 'price', 'purchase_time', 'is_paid')
    list_filter = ('is_paid', 'session__movie', 'session__start_time')
    search_fields = ('user__username', 'session__movie__title')

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent', 'code', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Hall, HallAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Discount, DiscountAdmin)
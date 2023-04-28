from django.contrib import admin
# Register your models here.

from django.contrib import admin

from users.models import EmailVerification, User, RequestMatchVerification, UsersMatches
from wish.admin import WishAdmin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_verified_email', 'is_matched')
    fields = (
        'first_name', 'last_name', 'username', 'email', 'is_verified_email', 'is_matched', 'matched_user', 'password')
    inlines = (WishAdmin,)



@admin.register(UsersMatches)
class UserMatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_main', 'user_requested',)
    fields = ('user_main', 'user_requested', 'created_at',)
    readonly_fields = ('user_main', 'user_requested', 'created_at',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'created', 'expiration',)
    fields = ('id', 'code', 'user', 'expiration')
    readonly_fields = ('id', 'created',)


@admin.register(RequestMatchVerification)
class RequestMatchVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_user', 'requested_user',)
    fields = ('main_user', 'requested_user', 'created_at', 'expiration',)
    readonly_fields = ('main_user', 'requested_user', 'created_at', 'expiration',)

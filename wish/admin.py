from django.contrib import admin

from wish.models import Wish, ActiveWish, HistoryExecutionWishes


# Register your models here.
@admin.register(Wish)
class WishesAdmin(admin.ModelAdmin):
    list_display = ('id', 'tittle',)
    fields = ('id', 'tittle', 'description', 'created_at', 'user')
    readonly_fields = ('id', 'tittle', 'description', 'created_at', 'user')


class WishAdmin(admin.TabularInline):
    model = Wish
    fields = ('id', 'tittle', 'description')
    readonly_fields = ('id', 'tittle', 'description')
    extra = 0


admin.site.register(ActiveWish)
admin.site.register(HistoryExecutionWishes)

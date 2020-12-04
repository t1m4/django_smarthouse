from django.contrib import admin

# Register your models here.
from core.models import Setting, Links

admin.site.register(Setting)
admin.site.register(Links)
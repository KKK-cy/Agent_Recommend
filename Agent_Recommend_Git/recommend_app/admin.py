from django.contrib import admin

# Register your models here.
from .models import Agents_other_info, Agents_comments,User

admin.site.register(Agents_other_info)
admin.site.register(Agents_comments)
admin.site.register(User)
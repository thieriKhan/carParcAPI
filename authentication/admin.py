from django.contrib import admin
from django.contrib.admin.forms import AdminPasswordChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, AdminUserCreationForm
from django.contrib.auth.models import  Permission
from django.contrib.contenttypes.models import ContentType

from authentication.models import  User

# Register your models here.

class UserAdmin(BaseUserAdmin):
 pass


filter_horizontal = ("groups", "user_permissions")

admin.site.register(Permission)

admin.site.register(ContentType)

admin.site.register(User, UserAdmin)



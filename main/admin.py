from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
from .models import User,Parent,Child


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email','password','username','ref_code','ref_link','last_login')}),
        ('Permisssions', {'fields' : (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups','user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide'),
                'fields': ('email', 'password')
            }
        ),
    )
    list_display = ('email', 'username','is_staff','last_login')
    list_filter = ('is_staff','is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)
admin.site.register(Parent)
admin.site.register(Child)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User, Employee, Role, Department

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employees'
    extra = 0
    fields = ('employee_first_name', 'employee_last_name', 'role', 'date_hired', 'employee_city', 'employee_county', 'employee_country', 'employee_post_code')


class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    inlines = (EmployeeInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_approved', 'user_actions')
    list_select_related = ('employee',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Additional Info'), {'fields': ('employee',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_approved')}
        ),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username', 'email')
    filter_horizontal = ('groups', 'user_permissions',)

    actions = ['approve_users']

    def user_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Approve</a>&nbsp;',
            reverse('admin:user_approve', args=[obj.pk]),
        )
    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True, is_active=True)
        # Here you might want to send an email to each user that has been approved
    approve_users.short_description = "Approve selected users"

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'location')
    search_fields = ('department_name',)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_title', 'role_description')
    search_fields = ('role_title',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_first_name', 'employee_last_name', 'role', 'date_hired', 'employee_city', 'user_link')
    search_fields = ('employee_first_name', 'employee_last_name')
    list_filter = ('role', 'employee_city', 'employee_county')

    def user_link(self, obj):
        if obj.user:
            link = reverse("admin:auth_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user.username)
        return "-"
    user_link.short_description = 'Linked User'

admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Employee, EmployeeAdmin)




    



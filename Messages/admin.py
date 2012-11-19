from Messages.models import User
from Messages.models import Group
from Messages.models import Thread
from Messages.models import Message
from Messages.models import ReadMessage
from Messages.models import ArchivedThread
from django.contrib import admin


class GroupInline(admin.TabularInline):
	model = Group

class UserInline(admin.TabularInline):
	model = User

class UserAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,		{'fields': ['first_name']}),
		(None,		{'fields': ['last_name']}),
		(None,		{'fields': ['primary_email']}),
		(None,		{'fields': ['primary_phone']})
	]
	list_display = ('name', 'primary_email', 'primary_phone')

class GroupAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,		{'fields': ['name']})
	]
	list_display = ('name', 'member_count')

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
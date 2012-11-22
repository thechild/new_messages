from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from Messages.models import User, Group, Thread, Message

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_messages.views.home', name='home'),
    # url(r'^test_messages/', include('test_messages.foo.urls')),

    url(r'^user/(\d+)/$', 'Messages.views.user_messages'),
    url(r'^user/(\d+)/thread/(\d+)/$', 'Messages.views.view_thread_as_user', name='thread_detail'),
    url(r'^user/(\d+)/thread/(\d+)/post/$', 'Messages.views.new_message'),
    url(r'^user/(\d+)/group/(\d+)/$', 'Messages.views.view_group_as_user', name='group_detail'),
    url(r'^user/(\d+)/group/(\d+)/edit/$', 'Messages.views.edit_group', name='edit_group'),
    url(r'^user/(\d+)/new/$', 'Messages.views.new_thread', name='new_thread'),
    url(r'^user/(\d+)/new_member/$', 'Messages.views.new_member'),
    url(r'^user/(\d+)/user/(\d+)/$', 'Messages.views.view_user'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

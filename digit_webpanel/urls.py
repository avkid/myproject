from django.conf.urls.defaults import *

from django.contrib import admin
import control_panel.admin
import django.contrib.auth.admin
# Uncomment the next two lines to enable the admin:
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    # Example:
    # (r'^digit_webpanel/', include('digit_webpanel.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:    
)

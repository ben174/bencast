from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'bencast.views.hs_feed', name='feed'),
    url(r'^hs$', 'bencast.views.hs_feed', name='hs'),
    url(r'^hh$', 'bencast.views.hh_feed', name='hh'),
    url(r'^al$', 'bencast.views.al_feed', name='hl'),
)

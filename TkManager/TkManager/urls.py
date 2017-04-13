from django.contrib.auth.views import login, logout, password_change
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic import RedirectView
admin.autodiscover()

from TkManager.util import common_view


urlpatterns = patterns('',

    #url(r'^$', 'TkManager.user.getViewByUser'),
    url(r'^$',  RedirectView.as_view(url='/order')),
    url(r'^order/', include('TkManager.order.urls')),
    url(r'^review/', include('TkManager.review.urls')),
    url(r'^operation/', include('TkManager.operation.urls')),
    url(r'^collection/', include('TkManager.collection.urls')),
    url(r'^custom/', include('TkManager.custom.urls')),
    url(r'^audit/', include('TkManager.audit.urls')),

    ## other pages
    (r'^thanks', TemplateView.as_view(template_name='common/404.html')),
    (r'^help', TemplateView.as_view(template_name='common/404.html')),
    (r'^feedback', TemplateView.as_view(template_name='common/404.html')),

    ## admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    ## account
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logged_out/$', logout),
    url(r'^accounts/change_password/$', password_change, {'post_change_redirect':'/'}),
)

#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )

handler403 = common_view.forbidden_view

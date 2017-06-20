from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create$', views.createContactList, name='create'),
    url(r'^populateSenators$', views.populateSenators, name='populateSenators'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

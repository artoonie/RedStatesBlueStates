from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create$', views.createContactList, name='create'),
    url(r'^combine$', views.combineContactList, name='combine'),
    url(r'^initialize$', views.populateSenators, name='populateSenators'),
    url(r'^fixCities$', views.updateCitiesAndStatesWithLatestData, name='fixCities'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

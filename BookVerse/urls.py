
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from .views import *

urlpatterns = [
    path('', mainHomePage, name='mainHomePage'),
    path('admin/', admin.site.urls),
    path('books/', include("books.urls")),
    path('accounts/', include('users.urls')),
    path('reviews/', include('reviews.urls')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),
]

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
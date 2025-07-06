from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as users_views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', include("mainpages.urls")),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),
    path('admin/', admin.site.urls),
    path('account/', include("users.urls")),
    path('books/', include("book.urls")),
    path('agent/', include("agent.urls")),
]

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
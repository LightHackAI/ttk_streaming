from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import RedirectView
from app import settings

urlpatterns = [
    path('myttk_streaming/admin/', admin.site.urls),
    path('myttk_streaming/', include('player.urls', namespace='player')),
    path('myttk_streaming/accounts/', include('accounts.urls', namespace='accounts')),
    path('', RedirectView.as_view(url='/myttk_streaming/player/', permanent=False)),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
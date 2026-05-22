from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 1. 先把所有 core 里的路由都包含进来
    path('', include('core.urls')),
    # 2. 再设置根路径的跳转（必须放在 include 后面）
    path('', RedirectView.as_view(url='/login/')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
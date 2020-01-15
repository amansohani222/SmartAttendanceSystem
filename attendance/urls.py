from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from attendance import views
from attendance.views import LogoutView

router = DefaultRouter()
router.register(r'officers', views.OfficerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/login/', obtain_auth_token),
    path('api/v1/logout/', LogoutView.as_view()),
    path('api/v1/', include(router.urls)),

]

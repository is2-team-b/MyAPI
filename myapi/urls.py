"""myapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework_mongoengine import routers
from config.views import *

# this is DRF router for REST API viewsets
router = routers.DefaultRouter()

# register REST API endpoints with DRF router
router.register(r'user', UserViewSet, r"user")
router.register(r'match', MatchViewSet, r"match")
router.register(r'stage', StageViewSet, r"stage")
router.register(r'login', LoginViewSet, r"login")
router.register(r'config', ConfigViewSet, r"config")

urlpatterns = [
    # default django admin interface
    url(r'^admin/', include(admin.site.urls)),

    # REST API root view (generated by DRF router)
    url(r'^api/', include(router.urls, namespace='api')),

    # config interface
    url(r'', 'template/config.html')
]

"""ASF URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from user import views

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^login', views.login, name='login'),
    url(r'^signup', views.aadharveri, name='aadharveri'),
    url(r'^info', views.info, name='info'),
    url('home', views.home, name="home"),
    url(r'^meet', views.meet, name="meet"),
    url("aboutus", views.aboutus, name="aboutus"),
    url(r'^listofvol', views.vnear, name="vnear"),
    url("schedule", views.schedule, name="schedule"),
    url("help", views.steps, name="steps"),
    url("events", views.events, name="events"),
    url(r'^', views.homepage, name="homepage"),
]


urlpatterns += static(settings.MEDIA_URL, documents_root=settings.MEDIA_URL)

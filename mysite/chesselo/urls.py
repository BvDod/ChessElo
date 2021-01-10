"""mysite URL Configuration

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
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path("index", views.index, name="index"),
    path("leaderboards", views.leaderboards, name="leaderboards"),
    path("logout", views.logout_view, name="account"),
    path("logout/", views.logout_view, name="account"),
    path("pending", views.pending, name="pending"),
    path("account", views.account, name="account"),
    path("account/", views.account, name="account"),
    path("account/<str:username>", views.account, name="account"),
    path("account/<str:username>/", views.account, name="account"),
    path("add_match", views.add_match, name="add_match"),
    path("accept", views.accept, name="accept"),
    path("cancel_match", views.cancel, name="cancel_match"),
]
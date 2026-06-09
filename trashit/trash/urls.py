"""trash URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path(r'report_trash/', views.ReportTrash.as_view(), name='report_trash'),
    path(r'report_dump/', views.ReportDump.as_view(), name='report_dump'),
    path('garbage_collection/', views.GarbageCollection.as_view(), name='garbage_collection'),
    path('scan_wrapper/', views.ScanWrapper.as_view(), name='scan_wrapper'),
    path(r'create-trash/', views.CreateTrash, name='create_trash'),
]

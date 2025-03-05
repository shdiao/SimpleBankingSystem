#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/create/', views.create_account, name='create_account'),
    path('accounts/<int:account_id>/deposit/', views.deposit, name='deposit'),
    path('accounts/<int:account_id>/withdraw/', views.withdraw, name='withdraw'),
    path('accounts/<int:account_id>/transfer/', views.transfer, name='transfer'),
    path('save_csv/', views.save_to_csv, name='save_csv'),
    path('load_csv/', views.load_from_csv, name='load_csv'),
]
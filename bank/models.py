#! /usr/bin/env python

from django.db import models

# Create your models here.

class Account(models.Model):
    account_name = models.CharField(max_length=100, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.account_name

#! /usr/bin/env python

import json
from django.urls import reverse
from django.test import TestCase, Client

from .models import Account

# Create your tests here.

class BankAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.account1 = Account.objects.create(account_name='Test Account 1', balance=100.00)
        self.account2 = Account.objects.create(account_name='Test Account 2', balance=50.00)

    def test_create_account(self):
        url = reverse('create_account')
        data = {'account_name': 'New Account', 'initial_balance': 200.00}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Account.objects.count(), 3)

    def test_account_list(self):
        url = reverse('account_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_deposit(self):
        url = reverse('deposit', args=[self.account1.id])
        data = {'amount': 50.00}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, 150.00)

    def test_withdraw(self):
        url = reverse('withdraw', args=[self.account1.id])
        data = {'amount': 20.00}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, 80.00)

    def test_withdraw_insufficient_funds(self):
        url = reverse('withdraw', args=[self.account2.id])
        data = {'amount': 100.00}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_transfer(self):
        url = reverse('transfer', args=[self.account1.id])
        data = {'to_account_id': self.account2.id, 'amount': 30.00}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, 70.00)
        self.assertEqual(self.account2.balance, 80.00)

    def test_transfer_insufficient_funds(self):
        url = reverse('transfer', args=[self.account2.id])
        data = {'to_account_id': self.account1.id, 'amount': 100.00}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_save_to_csv(self):
        url = reverse('save_csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')

    # def test_load_from_csv(self):
    #     url = reverse('load_csv')
    #     csv_data = 'Account Name,Balance\nAccount 3,300.00\nAccount 4,400.00'
    #     response = self.client.post(url, {'csv_file': ('test.csv', csv_data, 'text/csv')})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(Account.objects.count(), 2)

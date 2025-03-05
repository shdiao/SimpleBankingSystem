#! /usr/bin/env python

import json
import csv
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Account
# Create your views here.


@csrf_exempt
def create_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            account_name = data['account_name']
            initial_balance = Decimal(data['initial_balance'])
            account = Account.objects.create(account_name=account_name, balance=initial_balance)
            return JsonResponse(
                {'id': account.id, 'account_name': account.account_name, 'balance': Decimal(account.balance)},
                status=201)
        except (json.JSONDecodeError, KeyError, ValueError):
            return JsonResponse({'error': 'Invalid request data'}, status=400)
        except BaseException as e:
            return JsonResponse({'error': f'Request errr, {e}'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def account_list(request):
    accounts = Account.objects.all()
    data = [{'id': account.id, 'account_name': account.account_name, 'balance': Decimal(account.balance)} for account in
            accounts]
    return JsonResponse(data, safe=False)


@csrf_exempt
def deposit(request, account_id):
    account = Account.objects.get(pk=account_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = Decimal(data['amount'])
            account.balance += amount
            account.save()
            return JsonResponse(
                {'id': account.id, 'account_name': account.account_name, 'balance': Decimal(account.balance)})
        except (json.JSONDecodeError, KeyError, ValueError):
            return JsonResponse({'error': 'Invalid request data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def withdraw(request, account_id):
    account = Account.objects.get(pk=account_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = Decimal(data['amount'])
            if account.balance >= amount:
                account.balance -= amount
                account.save()
                return JsonResponse(
                    {'id': account.id, 'account_name': account.account_name, 'balance': Decimal(account.balance)})
            else:
                return JsonResponse({'error': 'Insufficient funds'}, status=400)
        except (json.JSONDecodeError, KeyError, ValueError):
            return JsonResponse({'error': 'Invalid request data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def transfer(request, account_id):
    from_account = Account.objects.get(pk=account_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            to_account_id = data['to_account_id']
            to_account = Account.objects.get(pk=to_account_id)
            amount = Decimal(data['amount'])
            if from_account.balance >= amount:
                from_account.balance -= amount
                to_account.balance += amount
                from_account.save()
                to_account.save()
                return JsonResponse({'message': 'Transfer successful'})
            else:
                return JsonResponse({'error': 'Insufficient funds'}, status=400)
        except (json.JSONDecodeError, KeyError, ValueError, Account.DoesNotExist):
            return JsonResponse({'error': 'Invalid request data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def save_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bank_accounts.csv"'
    writer = csv.writer(response)
    writer.writerow(['Account Name', 'Balance'])
    accounts = Account.objects.all()
    for account in accounts:
        writer.writerow([account.account_name, account.balance])
    return response


@csrf_exempt
def load_from_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        next(reader)
        Account.objects.all().delete()  # 清空所有账户
        for row in reader:
            Account.objects.create(account_name=row[0], balance=row[1])
        return JsonResponse({'message': 'CSV loaded successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

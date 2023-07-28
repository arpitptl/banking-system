from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from ..models import User, Bank, Account


class CreateAccountAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a test user object
        self.user = User.objects.create(name='Test User', address='Test Address')

        # Create a test bank object
        self.bank = Bank.objects.create(name='Test Bank')

    def test_create_account(self):
        url = reverse('create_account')
        data = {
            "account_number": "A123456789",
            "account_type": "regular_saving",
            "balance": 10000,
            "user": self.user.id,
            "bank": self.bank.id,
        }
        print(self.user, self.bank)
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user(self):
        url = reverse('create_user')
        data = {
            "name": "New User",
            "address": "New Address",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bank(self):
        url = reverse('create_bank')
        data = {
            "name": "New Bank",
            "location": "India"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DepositWithdrawAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(name='Test User', address='Test Address')
        self.bank = Bank.objects.create(name='Test Bank')
        self.account = Account.objects.create(
            account_number='A123456789',
            account_type='regular_saving',
            balance=10000,
            user=self.user,
            bank=self.bank
        )

    def test_deposit_api(self):
        url = reverse('deposit', kwargs={'account_id': self.account.id})
        data = {
            "amount": 5000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Deposit successful')
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 15000)

    def test_withdraw_api(self):
        url = reverse('withdraw', kwargs={'account_id': self.account.id})
        data = {
            "amount": 5000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Withdrawal successful')
        self.account.refresh_from_db()
        self.assertEqual(int(self.account.balance), 5000)

    def test_withdraw_insufficient_balance(self):
        url = reverse('withdraw', kwargs={'account_id': self.account.id})
        data = {
            "amount": 15000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("response.data['error']: ", response.data['error'])
        self.assertEqual(response.data['error'], 'Withdrawal failed because Insufficient balance in your account')
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 10000)

    def test_withdraw_invalid_account(self):
        url = reverse('withdraw', kwargs={'account_id': 9999})
        data = {
            "amount": 5000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Account not found')

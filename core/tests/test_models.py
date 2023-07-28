from django.test import TestCase
from ..models import Account, Transaction, User, Bank


class AccountModelTestCase(TestCase):
    def setUp(self):
        # Create test user and bank objects
        self.user = User.objects.create(name='Test User', address='Test Address')
        self.bank = Bank.objects.create(name='Test Bank')

        # Create a test account
        self.account = Account.objects.create(
            account_number='A123456789',
            account_type='regular_saving',
            balance=10000,
            user=self.user,
            bank=self.bank
        )

    def test_deposit(self):
        initial_balance = self.account.balance
        amount = 2000
        self.account.deposit(amount)
        self.assertEqual(self.account.balance, initial_balance + amount)

    def test_withdraw(self):
        initial_balance = self.account.balance
        amount = 2000
        self.account.withdraw(amount)
        self.assertEqual(self.account.balance, initial_balance - amount)

    def test_withdraw_limit(self):
        # Test withdrawal limit for regular_saving account
        self.account.account_type = 'regular_saving'
        self.account.save()
        for i in range(10):
            self.assertTrue(self.account.withdraw(1000)[0])  # Withdrawal charge is 0 for first 10 withdrawals
        self.assertFalse(self.account.withdraw(1000)[0])  # Withdrawal charge should be applied

    def test_transaction_history(self):
        # Create some test transactions
        Transaction.objects.create(account=self.account, amount=1000, transaction_type='deposit', available_balance_after_transaction=self.account.balance)
        Transaction.objects.create(account=self.account, amount=500, transaction_type='withdrawal', available_balance_after_transaction=self.account.balance)
        Transaction.objects.create(account=self.account, amount=1500, transaction_type='deposit', available_balance_after_transaction=self.account.balance)

        # Test transaction history
        transaction_history = self.account.transactions.all()
        self.assertEqual(len(transaction_history), 3)

    def test_kyc_update(self):
        initial_kyc_verified = self.account.kyc_verified
        self.account.update_kyc_status(True)
        self.assertNotEqual(initial_kyc_verified, self.account.kyc_verified)
        self.assertTrue(self.account.kyc_verified)

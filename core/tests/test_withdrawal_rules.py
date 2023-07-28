from django.test import TestCase
from ..models import Account, User, Bank, Transaction


class WithdrawalRulesTestCase(TestCase):
    def setUp(self):
        # Create a test user and bank objects
        self.user = User.objects.create(name='Test User', address='Test Address')
        self.bank = Bank.objects.create(name='Test Bank')

    def create_account(self, account_type, balance, min_balance=0):
        return Account.objects.create(
            account_number='A123456789',
            account_type=account_type,
            balance=balance,
            user=self.user,
            bank=self.bank
        )

    def create_transaction(self, account, amount, transaction_type='withdrawal'):
        return Transaction.objects.create(account=account, amount=amount, transaction_type=transaction_type, available_balance_after_transaction=account.balance)

    def test_zero_balance_account_withdrawal_limit(self):
        zero_balance_account = self.create_account(account_type='zero_balance', balance=1000)

        # Perform 4 withdrawals, which should be allowed
        for _ in range(4):
            self.assertTrue(zero_balance_account.withdraw(100))

        # The 5th withdrawal should be blocked
        self.assertFalse(zero_balance_account.withdraw(100)[0])

    def test_student_account_withdrawal_limit(self):
        student_account = self.create_account(account_type='student', balance=5000)

        # Perform 4 withdrawals, which should be allowed
        for _ in range(4):
            self.assertTrue(student_account.withdraw(1000)[0])

        # The 5th withdrawal should be blocked
        self.assertFalse(student_account.withdraw(1000)[0])

    def test_student_account_min_balance_limit(self):
        student_account = self.create_account(account_type='student', balance=2000)

        # Withdrawal beyond the min balance should be blocked
        self.assertFalse(student_account.withdraw(2000)[0])

    def test_regular_saving_account_withdrawal_limit(self):
        regular_saving_account = self.create_account(account_type='regular_saving', balance=12000)

        # Perform 10 withdrawals, which should be allowed without any charge
        for _ in range(10):
            self.assertTrue(regular_saving_account.withdraw(500)[0])

        # The 11th withdrawal should be allowed but with a charge of 5 rupees
        self.assertTrue(regular_saving_account.withdraw(500)[0])
        self.assertEqual(regular_saving_account.balance, 6495)  # 12000 - 5000 - 5

    def test_regular_saving_account_withdrawal_charge(self):
        regular_saving_account = self.create_account(account_type='regular_saving', balance=15000)

        # Perform 15 withdrawals
        for _ in range(15):
            self.assertTrue(regular_saving_account.withdraw(500)[0])

        # The balance should be reduced by 7525 rupees (5 extra withdrawals x 5 rupees charge each + 7500)
        self.assertEqual(regular_saving_account.balance, 7475)  # 15000 - (5*5 + 7500)

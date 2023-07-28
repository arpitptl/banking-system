from django.test import TestCase
from ..models import Account, User, Bank


class DepositRulesTestCase(TestCase):
    def setUp(self):
        # Create a test user and bank objects
        self.user = User.objects.create(name='Test User', address='Test Address')
        self.bank = Bank.objects.create(name='Test Bank')

    def create_account(self, account_type, balance, kyc_verified=False):
        return Account.objects.create(
            account_number='A123456789',
            account_type=account_type,
            balance=balance,
            user=self.user,
            bank=self.bank,
            kyc_verified=kyc_verified
        )

    def test_student_account_max_monthly_deposit(self):
        student_account = self.create_account(account_type='student', balance=5000)

        # Deposit 10,000 rupees, which should be allowed
        self.assertTrue(student_account.deposit(10000)[0])
        self.assertEqual(student_account.balance, 15000)  # 5000 + 10000

        # Depositing more than 10,000 in the same month should fail
        self.assertFalse(student_account.deposit(2000)[0])
        self.assertEqual(student_account.balance, 15000)  # Should remain the same

    def test_regular_saving_account_kyc_required(self):
        regular_saving_account = self.create_account(account_type='regular_saving', balance=10000)

        # Depositing less than 50,000 should be allowed without KYC flag
        self.assertTrue(regular_saving_account.deposit(1000)[0])
        self.assertEqual(regular_saving_account.balance, 11000)  # 10000 + 1000

        # Depositing 50,000 should fail without KYC flag
        self.assertFalse(regular_saving_account.deposit(51000)[0])
        self.assertEqual(regular_saving_account.balance, 11000)  # Should remain the same

        # Set KYC flag to True
        regular_saving_account.kyc_verified = True
        regular_saving_account.save()

        # Depositing 50,000 should now be allowed with KYC flag
        self.assertTrue(regular_saving_account.deposit(51000)[0])
        self.assertEqual(regular_saving_account.balance, 62000)  # 11000 + 51000

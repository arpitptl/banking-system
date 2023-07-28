from datetime import datetime, timedelta
from django.db.models import Avg
from django.db import models
from .constants import AccountConstants, WithdrawalConstant, StudentAccountWithdrawalConstant, \
    SavingAccountWithdrawalConstant, DepositConstant, StudentAccountDepositConstant


class Bank(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class User(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Account(models.Model):
    account_number = models.CharField(max_length=50, unique=True)
    account_type = models.CharField(max_length=20, choices=AccountConstants.ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    kyc_verified = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='accounts')

    def __str__(self):
        return f"{self.account_number} - {self.account_type} - {self.user} - {self.bank}"

    def get_balance(self):
        return self.balance

    def update_kyc_status(self, kyc_verified):
        self.kyc_verified = kyc_verified
        self.save()

    def deposit(self, amount):
        strategy = self._get_deposit_strategy()
        deposit_allowed, reason = strategy.is_allowed(self, amount)
        if deposit_allowed:
            self.balance += amount
            self.save()
            Transaction.objects.create(account=self, amount=amount, transaction_type='deposit',
                                       available_balance_after_transaction=self.balance)
            return True, ''
        return False, reason

    def withdraw(self, amount):
        strategy = self._get_withdrawal_strategy()
        withdrawal_allowed, reason = strategy.is_allowed(self, amount)
        if withdrawal_allowed:
            withdrawal_charge = 0
            if self.account_type == 'regular_saving':
                withdrawal_charge = strategy.calculate_withdrawal_charge(self)

            total_withdrawal_amount = amount + withdrawal_charge
            if self.balance >= total_withdrawal_amount:
                self.balance -= total_withdrawal_amount
                self.save()
                Transaction.objects.create(account=self, amount=total_withdrawal_amount, transaction_type='withdrawal',
                                           available_balance_after_transaction=self.balance)
                return True, ''
            else:
                reason = WithdrawalConstant.FAILURE_REASONS["INSUFFICIENT_BALANCE"]
        return False, reason

    def _get_withdrawal_strategy(self):
        withdrawal_strategies = {
            'zero_balance': ZeroBalanceWithdrawal(),
            'student': StudentWithdrawal(),
            'regular_saving': RegularSavingWithdrawal(),
        }
        return withdrawal_strategies.get(self.account_type)

    def _get_deposit_strategy(self):
        deposit_strategies = {
            'student': StudentDeposit(),
        }
        return deposit_strategies.get(self.account_type, DefaultDeposit())


class WithdrawalStrategy(models.Model):
    """
    Abstract base class for withdrawal strategies.
    Subclasses must implement the `is_allowed` method.
    """
    class Meta:
        abstract = True

    def is_allowed(self, account, amount):
        """
        Check if a withdrawal is allowed for the given account and amount.

        Parameters:
        - account: The Account instance for the withdrawal.
        - amount: The amount to be withdrawn.

        Returns:
        - A tuple containing a boolean value indicating if the withdrawal is allowed,
          and a reason string if the withdrawal is not allowed.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class ZeroBalanceWithdrawal(WithdrawalStrategy):
    """
    Withdrawal strategy for accounts with zero balance.
    Allows only a limited number of withdrawals per month.
    """
    def is_allowed(self, account, amount):
        withdrawal_count = account.transactions.filter(
            transaction_type='withdrawal',
            timestamp__month=datetime.now().month,
        ).count()
        if withdrawal_count >= WithdrawalConstant.MONTHLY_WITHDRAWAL_LIMIT:
            return False, WithdrawalConstant.FAILURE_REASONS["MONTHLY_WITHDRAWAL_LIMIT_BREACHED"]
        return True, ''


class StudentWithdrawal(WithdrawalStrategy):
    """
    Withdrawal strategy for student accounts.
    Allows only a limited number of withdrawals per month and enforces a minimum account balance.
    """
    def is_allowed(self, account, amount):
        withdrawal_count = account.transactions.filter(
            transaction_type='withdrawal',
            timestamp__month=datetime.now().month,
        ).count()

        if withdrawal_count >= StudentAccountWithdrawalConstant.MONTHLY_WITHDRAWAL_LIMIT:
            return False, WithdrawalConstant.FAILURE_REASONS["MONTHLY_WITHDRAWAL_LIMIT_BREACHED"]
        elif account.balance - amount < StudentAccountWithdrawalConstant.MIN_ACCOUNT_BALANCE:
            return False, WithdrawalConstant.FAILURE_REASONS["MIN_ACCOUNT_BALANCE_BREACHED"]

        return True, ''


class RegularSavingWithdrawal(WithdrawalStrategy):
    """
    Withdrawal strategy for regular saving accounts.
    Allows a limited number of free withdrawals per month and enforces a minimum average balance over the last 90 days.
    """
    def is_allowed(self, account, amount):
        # Check if the account has a minimum average balance of 5000 rupees over the last 90 days
        last_90_days = datetime.now() - timedelta(days=90)
        average_balance = account.transactions.filter(
            timestamp__gte=last_90_days,
        ).aggregate(avg_balance=Avg('available_balance_after_transaction'))['avg_balance']

        if average_balance and average_balance < SavingAccountWithdrawalConstant.AVERAGE_BALANCE:
            return False, WithdrawalConstant.FAILURE_REASONS["MIN_ACCOUNT_BALANCE_BREACHED"]

        return True, ''

    def calculate_withdrawal_charge(self, account):
        withdrawal_count = account.transactions.filter(
            transaction_type='withdrawal',
            timestamp__month=datetime.now().month,
        ).count()
        if withdrawal_count >= SavingAccountWithdrawalConstant.MONTHLY_WITHDRAWAL_LIMIT:
            return SavingAccountWithdrawalConstant.EXTRA_WITHDRAWAL_CHARGE
        return 0


class DepositStrategy(models.Model):
    """
    Abstract base class for deposit strategies.
    Subclasses must implement the `is_allowed` method.
    """
    class Meta:
        abstract = True

    def is_allowed(self, account, amount):
        """
        Check if a deposit is allowed for the given account and amount.

        Parameters:
        - account: The Account instance for the deposit.
        - amount: The amount to be deposited.

        Returns:
        - A tuple containing a boolean value indicating if the deposit is allowed,
          and a reason string if the deposit is not allowed.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class DefaultDeposit(DepositStrategy):
    def is_allowed(self, account, amount):
        if amount <= DepositConstant.DEPOSIT_LIMIT_WITHOUT_KYC:
            return True, ''
        elif account.kyc_verified:
            return True, ''
        return False, DepositConstant.FAILURE_REASONS["KYC_LIMIT_BREACHED"]


class StudentDeposit(DepositStrategy):
    """
    Deposit strategy for student accounts.
    Limits the total deposit amount in a month.
    """
    def is_allowed(self, account, amount):
        # Check if the total deposit amount in this month exceeds the monthly limit (10,000 rupees)
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        total_deposit_this_month = account.transactions.filter(
            transaction_type='deposit',
            timestamp__gte=first_day_of_month,
            timestamp__lte=today
        ).aggregate(total_deposit=models.Sum('amount'))['total_deposit'] or 0

        if total_deposit_this_month + amount > StudentAccountDepositConstant.MONTHLY_DEPOSIT_LIMIT:
            return False, DepositConstant.FAILURE_REASONS["MONTHLY_DEPOSIT_LIMIT_BREACHED"]

        return True, ''


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    available_balance_after_transaction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"

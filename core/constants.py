class AccountConstants:
    ACCOUNT_TYPES = (
        ('zero_balance', 'Zero Balance Account'),
        ('student', 'Student Account'),
        ('regular_saving', 'Regular Saving Account'),
    )


class WithdrawalConstant:
    MONTHLY_WITHDRAWAL_LIMIT = 4
    FAILURE_REASONS = {
        "MONTHLY_WITHDRAWAL_LIMIT_BREACHED": "Monthly withdrawal limit is exceeded.",
        "MIN_ACCOUNT_BALANCE_BREACHED": "You do not have min account balance.",
        "INSUFFICIENT_BALANCE": "Insufficient balance in your account"
    }


class StudentAccountWithdrawalConstant(WithdrawalConstant):
    MIN_ACCOUNT_BALANCE = 1000


class SavingAccountWithdrawalConstant(WithdrawalConstant):
    MONTHLY_WITHDRAWAL_LIMIT = 10
    AVERAGE_BALANCE = 5000
    EXTRA_WITHDRAWAL_CHARGE = 5


class DepositConstant:
    DEPOSIT_LIMIT_WITHOUT_KYC = 50000
    FAILURE_REASONS = {
        "MONTHLY_DEPOSIT_LIMIT_BREACHED": "Monthly deposit limit is exceeded.",
        "KYC_LIMIT_BREACHED": "You don't have verified KYC to deposit this much amount"
    }


class StudentAccountDepositConstant(DepositConstant):
    MONTHLY_DEPOSIT_LIMIT = 10000

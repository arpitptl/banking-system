from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer, UserSerializer, BankSerializer


@api_view(['POST'])
def create_user(request):
    """
    Create a new user.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - Response with the created user data if successful, or error data if validation fails.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def create_bank(request):
    """
    Create a new bank.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - Response with the created bank data if successful, or error data if validation fails.
    """
    serializer = BankSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def create_account(request):
    """
    Create a new account (ZeroBalance, Student, or RegularSaving).

    Parameters:
    - request: The HTTP request object.

    Returns:
    - Response with the created account data if successful, or error data if validation fails.
    """
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def deposit(request, account_id):
    """
    Deposit money into an account.

    Parameters:
    - request: The HTTP request object.
    - account_id: The ID of the account to deposit money into.

    Returns:
    - Response with the success message and updated balance if deposit is successful,
      or error data if validation fails or deposit fails.
    """
    try:
        account = Account.objects.get(pk=account_id)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)

    amount = int(request.data.get('amount', 0))
    if amount <= 0:
        return Response({"error": "Invalid deposit amount"}, status=400)

    success, failed_reason = account.deposit(amount)
    if success:
        return Response({
            "message": "Deposit successful",
            "updated_balance": account.get_balance()}, status=200)
    error_message = f"Deposit failed because {failed_reason}"
    return Response({"error": error_message}, status=400)


@api_view(['POST'])
def withdraw(request, account_id):
    """
    Withdraw money from an account.

    Parameters:
    - request: The HTTP request object.
    - account_id: The ID of the account to withdraw money from.

    Returns:
    - Response with the success message and updated balance if withdrawal is successful,
      or error data if validation fails or withdrawal fails.
    """
    try:
        account = Account.objects.get(pk=account_id)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)

    amount = int(request.data.get('amount', 0))
    if amount <= 0:
        return Response({"error": "Invalid withdrawal amount"}, status=400)

    success, failed_reason = account.withdraw(amount)
    if success:
        return Response({"message": "Withdrawal successful",
                         "updated_balance": account.get_balance()}, status=200)
    error_message = f"Withdrawal failed because {failed_reason}"
    return Response({"error": error_message}, status=400)


@api_view(['GET'])
def transaction_history(request, account_id):
    """
    Retrieve transaction history for an account.

    Parameters:
    - request: The HTTP request object.
    - account_id: The ID of the account to retrieve transaction history for.

    Returns:
    - Response with the list of transaction data if successful, or error data if account is not found.
    """
    try:
        account = Account.objects.get(pk=account_id)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)

    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=200)


@api_view(['PATCH'])
def update_kyc_status(request, account_id):
    """
    Update the KYC status of an account.

    Parameters:
    - request: The HTTP request object.
    - account_id: The ID of the account to update the KYC status for.

    Returns:
    - Response with the success message if KYC status is updated successfully,
      or error data if account is not found or KYC flag is not provided.
    """
    try:
        account = Account.objects.get(pk=account_id)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)

    kyc_verified = request.data.get('kyc_verified', None)
    if kyc_verified is None:
        return Response({"error": "KYC flag not provided"}, status=400)

    account.update_kyc_status(kyc_verified)
    return Response({"message": "KYC status updated successfully"}, status=200)

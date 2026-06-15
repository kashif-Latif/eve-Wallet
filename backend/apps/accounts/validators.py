import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_phone(value):
    """
    Validate that the phone number is in a valid international format.
    Accepts formats: +1234567890, 1234567890 (10-15 digits)
    """
    if not value:
        raise ValidationError('Phone number is required.')

    # Remove any spaces or dashes
    cleaned = re.sub(r'[\s\-()]', '', value)

    # Validate format
    if not re.match(r'^\+?\d{9,15}$', cleaned):
        raise ValidationError(
            'Phone number must be 9-15 digits, optionally starting with +.'
        )

    return value


def validate_password_strength(value):
    """
    Validate that the password meets security requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(value) < 8:
        raise ValidationError(
            'Password must be at least 8 characters long.'
        )

    if len(value) > 128:
        raise ValidationError(
            'Password must be less than 128 characters long.'
        )

    if not re.search(r'[A-Z]', value):
        raise ValidationError(
            'Password must contain at least one uppercase letter.'
        )

    if not re.search(r'[a-z]', value):
        raise ValidationError(
            'Password must contain at least one lowercase letter.'
        )

    if not re.search(r'\d', value):
        raise ValidationError(
            'Password must contain at least one digit.'
        )

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':\"\\|,.<>\/?]', value):
        raise ValidationError(
            'Password must contain at least one special character (!@#$%^&* etc.).'
        )

    return value


def validate_wallet_number(value):
    """
    Validate that the wallet number is exactly 12 digits.
    """
    if not re.match(r'^\d{12}$', str(value)):
        raise ValidationError(
            'Wallet number must be exactly 12 digits.'
        )
    return value


def validate_amount(value):
    """
    Validate that the transaction amount is positive and within limits.
    """
    from decimal import Decimal

    if value is None:
        raise ValidationError('Amount is required.')

    amount = Decimal(str(value))

    if amount <= 0:
        raise ValidationError('Amount must be greater than zero.')

    if amount > Decimal('1000000'):
        raise ValidationError('Amount cannot exceed $1,000,000 per transaction.')

    return value

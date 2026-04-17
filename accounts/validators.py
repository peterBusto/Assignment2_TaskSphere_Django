import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Validates that the password meets the following requirements:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 number
    - At least 1 special character
    """
    
    def validate(self, password, user=None):
        # Check minimum length
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("Password must contain at least 1 uppercase letter."))
        
        # Check for at least one number
        if not re.search(r'\d', password):
            raise ValidationError(_("Password must contain at least 1 number."))
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', password):
            raise ValidationError(_("Password must contain at least 1 special character."))
    
    def get_help_text(self):
        return _(
            "Password should have at least 8 characters, 1 uppercase, 1 number and 1 special character for security purpose."
        )

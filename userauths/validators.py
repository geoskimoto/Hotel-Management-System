from django.core.validators import EmailValidator
from .models import ApprovedEmail

# Fetch the list of approved emails directly
def dynamic_email_allowlist():
    return list(ApprovedEmail.objects.values_list('email', flat=True))

# Pass the list, not the function, to EmailValidator
validate_email = EmailValidator(allowlist=dynamic_email_allowlist())

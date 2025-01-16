from django.core.exceptions import ValidationError

def validate_attachment_file_size(value):
    limit = 15 * 1024 * 1024  # 15 MB limit
    if value.size > limit:
        raise ValidationError(f'File too large. Size should not exceed {limit / (1024 * 1024)} MB.')

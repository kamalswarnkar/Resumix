from rest_framework.exceptions import ValidationError


MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_resume_file(uploaded_file):
    extension = "." + uploaded_file.name.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("Only PDF and DOCX files are supported")
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"File size must be <= {MAX_FILE_SIZE_MB}MB")

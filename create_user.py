import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyCurrency.settings")
django.setup()

User = get_user_model()


if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username="currency", email="currency@example.com", password="protectedpassword"
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")

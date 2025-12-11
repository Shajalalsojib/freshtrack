import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from freshtrack_project.freshtrack_app.models import Product

# Delete all products
deleted_count, _ = Product.objects.all().delete()
print(f"✅ Deleted {deleted_count} products!")
print("Database cleaned. Ready for real products.")

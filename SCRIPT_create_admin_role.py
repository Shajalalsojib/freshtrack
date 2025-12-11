import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from freshtrack_project.freshtrack_app.models import UserRole

# Create role for admin if not exists
admin = User.objects.get(username='admin')
try:
    role = admin.role
    print(f"Admin already has role: {role.role}")
except:
    UserRole.objects.create(user=admin, role='admin', is_approved='approved', approved_at=timezone.now())
    print(f"✓ Created admin role for {admin.username}")

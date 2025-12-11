import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshtrack_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from freshtrack_project.freshtrack_app.models import UserRole

# Approve all existing users
for user in User.objects.all():
    try:
        role = user.role
        if role.is_approved == 'pending':
            role.is_approved = 'approved'
            role.approved_at = timezone.now()
            role.save()
            print(f"✓ Approved: {user.username} ({role.role})")
        else:
            print(f"ℹ Already approved: {user.username} ({role.role})")
    except:
        print(f"⚠ No role for: {user.username}")

print("✅ User approval check complete!")

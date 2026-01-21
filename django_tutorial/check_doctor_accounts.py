import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_tutorial.settings')
django.setup()

from django.contrib.auth.models import User
from doctors.models import Doctors

print("=" * 60)
print("CHECKING DR. MAMOOTY'S ACCOUNT")
print("=" * 60)

# Check for Dr. Mamooty
username = 'drmamooty'
user = User.objects.filter(username=username).first()

if user:
    print(f"\n✓ User Account Found:")
    print(f"  - Username: {user.username}")
    print(f"  - Email: {user.email}")
    print(f"  - First Name: {user.first_name}")
    print(f"  - Last Name: {user.last_name}")
    print(f"  - Is Superuser: {user.is_superuser}")
    print(f"  - Is Staff: {user.is_staff}")
    print(f"  - Date Joined: {user.date_joined}")
    print(f"  - Last Login: {user.last_login}")
    
    # Check for linked doctor profile
    try:
        doctor = user.doctors
        print(f"\n✓ Doctor Profile Found:")
        print(f"  - Doctor Name: {doctor.doc_name}")
        print(f"  - Specialization: {doctor.doc_spec}")
        print(f"  - Department: {doctor.dep_name.dep_name}")
        print(f"  - Image: {doctor.doc_image}")
    except:
        print("\n✗ No doctor profile linked to this user")
else:
    print(f"\n✗ User '{username}' not found in database")

print("\n" + "=" * 60)
print("ALL DOCTORS IN DATABASE")
print("=" * 60)

doctors = Doctors.objects.all()
for doctor in doctors:
    print(f"\n{doctor.doc_name} ({doctor.doc_spec})")
    print(f"  - Department: {doctor.dep_name.dep_name}")
    if doctor.user:
        print(f"  - Linked User: {doctor.user.username}")
    else:
        print(f"  - No user account")

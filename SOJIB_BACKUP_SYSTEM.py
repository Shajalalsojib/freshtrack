"""
🔒 Sojib's Automatic Backup System
এই script automatically backup করবে যেকোনো file modify করার আগে
"""

import os
import shutil
from datetime import datetime

# Backup directory
BACKUP_DIR = "sojib_backups"

def create_backup_dir():
    """Backup directory তৈরি করে"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"✅ Backup directory তৈরি হয়েছে: {BACKUP_DIR}")

def get_next_backup_number():
    """পরবর্তী backup number খুঁজে বের করে"""
    if not os.path.exists(BACKUP_DIR):
        return 1
    
    existing_backups = os.listdir(BACKUP_DIR)
    max_num = 0
    
    for backup in existing_backups:
        if backup.startswith("sojib") and backup[5:].split("_")[0].isdigit():
            num = int(backup[5:].split("_")[0])
            max_num = max(max_num, num)
    
    return max_num + 1

def backup_file(file_path):
    """
    File এর backup তৈরি করে sojibX_filename.ext format এ
    
    Example:
        backup_file("views.py") → sojib1_views_2025-12-11_15-30.py
    """
    create_backup_dir()
    
    if not os.path.exists(file_path):
        print(f"❌ File পাওয়া যায়নি: {file_path}")
        return None
    
    # Next backup number
    backup_num = get_next_backup_number()
    
    # File info
    filename = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Backup filename: sojibX_filename_timestamp.ext
    backup_filename = f"sojib{backup_num}_{filename.replace('.', f'_{timestamp}.')}"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # Copy file
    shutil.copy2(file_path, backup_path)
    
    print(f"✅ Backup created: {backup_filename}")
    print(f"   Original: {file_path}")
    print(f"   Backup: {backup_path}")
    
    return backup_path

def backup_multiple_files(file_paths):
    """একসাথে multiple files এর backup নেয়"""
    print("\n" + "="*60)
    print("🔒 SOJIB'S BACKUP SYSTEM")
    print("="*60)
    
    backups = []
    for file_path in file_paths:
        backup_path = backup_file(file_path)
        if backup_path:
            backups.append(backup_path)
    
    print("\n" + "="*60)
    print(f"✅ Total {len(backups)} files backed up successfully!")
    print("="*60 + "\n")
    
    return backups

def restore_backup(backup_filename):
    """Backup থেকে file restore করে"""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup file পাওয়া যায়নি: {backup_filename}")
        return False
    
    # Extract original filename
    # sojib1_views_2025-12-11_15-30.py → views.py
    parts = backup_filename.split("_", 1)
    if len(parts) < 2:
        print(f"❌ Invalid backup filename format")
        return False
    
    original_name = "_".join(parts[1].split("_")[:-2]) + "." + parts[1].split(".")[-1]
    
    # Restore
    shutil.copy2(backup_path, original_name)
    print(f"✅ Restored: {backup_filename} → {original_name}")
    
    return True

def list_backups():
    """সব backups এর list দেখায়"""
    if not os.path.exists(BACKUP_DIR):
        print("📁 কোনো backup নেই")
        return
    
    backups = sorted(os.listdir(BACKUP_DIR))
    
    if not backups:
        print("📁 কোনো backup নেই")
        return
    
    print("\n" + "="*60)
    print("📋 ALL BACKUPS")
    print("="*60)
    
    for i, backup in enumerate(backups, 1):
        size = os.path.getsize(os.path.join(BACKUP_DIR, backup))
        print(f"{i}. {backup} ({size} bytes)")
    
    print("="*60 + "\n")


# ============================================
# USAGE EXAMPLES
# ============================================

if __name__ == "__main__":
    print("""
    🔒 Sojib's Backup System - Usage Guide
    =======================================
    
    1. Single file backup:
       backup_file("views.py")
    
    2. Multiple files backup:
       backup_multiple_files([
           "views.py",
           "models.py",
           "templates/home.html"
       ])
    
    3. List all backups:
       list_backups()
    
    4. Restore a backup:
       restore_backup("sojib1_views_2025-12-11_15-30.py")
    """)
    
    # Example usage
    choice = input("\nTest backup? (y/n): ")
    if choice.lower() == 'y':
        # Test backup করার জন্য এই script নিজেই backup নেয়
        backup_file(__file__)
        list_backups()

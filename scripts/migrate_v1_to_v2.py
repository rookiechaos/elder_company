#!/usr/bin/env python3
"""
Database Migration Script - From Version 1.0 to 2.0
Database migration script - upgrade from version 1.0 to 2.0

This script migrates existing data from version 1.0 to version 2.0:
- Creates default organization for existing users
- Migrates user data to organization structure
- Preserves all existing data
"""

import sys
import os
from pathlib import Path

# Repo root (services/) and backend/ (config, models, utils)
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "backend"))
sys.path.insert(0, str(_root))

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from utils.time_utils import utc_now
import uuid

from config.database import SessionLocal, get_engine
from models.database import (
    OrganizationDB, UserProfileDB, TranslationHistoryDB
)
from models.auth_models import UserAuthDB


def check_database_version(db: Session) -> str:
    """Check current database version"""
    try:
        # Check if organizations table exists
        result = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' "
                 "AND name='organizations'")
        )
        if result.fetchone():
            return "2.0"
        else:
            return "1.0"
    except Exception:
        return "unknown"


def create_default_organization(db: Session) -> str:
    """Create default organization for existing users"""
    # Check if default org already exists
    existing = db.query(OrganizationDB).filter(
        OrganizationDB.org_id == "default_org"
    ).first()
    
    if existing:
        print("✅ Default organization already exists")
        return existing.org_id
    
    # Create default organization
    default_org = OrganizationDB(
        org_id="default_org",
        name="Default Organization",
        name_ja="デフォルト組織",
        org_type="general",
        subscription_plan="basic",
        max_users=100,
        monthly_translation_limit=10000,
        is_active=True,
        created_at=utc_now()
    )
    
    db.add(default_org)
    db.commit()
    db.refresh(default_org)
    
    print(f"✅ Created default organization: {default_org.org_id}")
    return default_org.org_id


def migrate_user_profiles(db: Session, org_id: str) -> int:
    """Migrate existing user profiles to organization structure"""
    # Get all user profiles without org_id
    profiles = db.query(UserProfileDB).filter(
        UserProfileDB.org_id.is_(None)
    ).all()
    
    migrated_count = 0
    for profile in profiles:
        profile.org_id = org_id
        profile.updated_at = utc_now()
        migrated_count += 1
    
    db.commit()
    print(f"✅ Migrated {migrated_count} user profiles to organization")
    return migrated_count


def migrate_translation_history(db: Session, org_id: str) -> int:
    """Migrate translation history to organization structure"""
    # Get all translation history without org_id
    history = db.query(TranslationHistoryDB).filter(
        TranslationHistoryDB.org_id.is_(None)
    ).all()
    
    migrated_count = 0
    for record in history:
        record.org_id = org_id
        migrated_count += 1
    
    db.commit()
    print(f"✅ Migrated {migrated_count} translation history records")
    return migrated_count


def create_user_profiles_from_auth(db: Session, org_id: str) -> int:
    """Create user profiles for users who have auth but no profile"""
    # Get all auth users
    auth_users = db.query(UserAuthDB).all()
    
    created_count = 0
    for auth_user in auth_users:
        # Check if profile exists
        existing_profile = db.query(UserProfileDB).filter(
            UserProfileDB.user_id == auth_user.user_id
        ).first()
        
        if not existing_profile:
            # Create default profile
            profile = UserProfileDB(
                user_id=auth_user.user_id,
                org_id=org_id,
                name=auth_user.username or auth_user.email or "User",
                user_role="caregiver",
                is_active=auth_user.is_active,
                created_at=auth_user.created_at or utc_now()
            )
            db.add(profile)
            created_count += 1
    
    db.commit()
    print(f"✅ Created {created_count} user profiles from auth records")
    return created_count


def migrate_database():
    """Main migration function"""
    print("=" * 60)
    print("Database Migration: Version 1.0 → 2.0")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Check current version
        version = check_database_version(db)
        print(f"Current database version: {version}")
        
        if version == "2.0":
            print("✅ Database is already at version 2.0")
            print("No migration needed.")
            return True
        
        if version != "1.0":
            print(f"⚠️  Unknown database version: {version}")
            response = input(
                "Continue with migration? (yes/no): "
            ).strip().lower()
            if response != "yes":
                print("Migration cancelled.")
                return False
        
        print()
        print("Starting migration...")
        print()
        
        # Step 1: Initialize database tables (if needed)
        print("[Step 1] Initializing database tables...")
        from config.database import init_database
        init_database()
        print("✅ Database tables initialized")
        print()
        
        # Step 2: Create default organization
        print("[Step 2] Creating default organization...")
        org_id = create_default_organization(db)
        print()
        
        # Step 3: Migrate user profiles
        print("[Step 3] Migrating user profiles...")
        profile_count = migrate_user_profiles(db, org_id)
        print()
        
        # Step 4: Create profiles for auth-only users
        print("[Step 4] Creating profiles for auth users...")
        created_count = create_user_profiles_from_auth(db, org_id)
        print()
        
        # Step 5: Migrate translation history
        print("[Step 5] Migrating translation history...")
        history_count = migrate_translation_history(db, org_id)
        print()
        
        # Summary
        print("=" * 60)
        print("Migration Summary")
        print("=" * 60)
        print(f"✅ Default organization created: {org_id}")
        print(f"✅ User profiles migrated: {profile_count}")
        print(f"✅ User profiles created: {created_count}")
        print(f"✅ Translation history migrated: {history_count}")
        print()
        print("✅ Migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Update your .env file with organization settings")
        print("2. Configure organization details via API")
        print("3. Review and update user-organization assignments")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Enhanced debug test for production environment configuration
Run this to test config and env file loading for any environment
"""
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Allow environment to be set via command line or default to production
target_env = sys.argv[1] if len(sys.argv) > 1 else "production"
os.environ["ENVIRONMENT"] = target_env

print(f"🔍 DEBUGGING ENV FILE LOADING - ENVIRONMENT: {target_env.upper()}")
print("=" * 60)

# Check current working directory
print(f"Current working directory: {os.getcwd()}")

# Check the base directory calculation (FIXED)
config_file = Path(__file__).parent / "src" / "core" / "config.py"
print(f"Config file path: {config_file}")

# CORRECTED BASE_DIR calculation - should point to backend/ directory
BASE_DIR = Path(__file__).parent  # This script is in backend/, so parent is backend/
print(f"BASE_DIR (corrected): {BASE_DIR}")
print(f"BASE_DIR absolute: {BASE_DIR.absolute()}")

# Environment-specific file mapping
env_file_map = {
    "development": ".env",
    "production": ".env.production", 
    "testing": ".env.testing",
}

# Check relevant env files
env_files_to_check = [
    BASE_DIR / env_file_map.get(target_env, ".env"),  # Target environment file
    BASE_DIR / ".env",                                # Fallback .env
    BASE_DIR / ".env.example",                        # Template file
]

print(f"\n📁 CHECKING ENV FILES FOR {target_env.upper()}:")
target_env_file = None
for env_file in env_files_to_check:
    abs_path = env_file.absolute()
    exists = env_file.exists()
    is_target = env_file.name == env_file_map.get(target_env, ".env")
    marker = "🎯 TARGET" if is_target else "📄"
    
    print(f"  {marker} {abs_path}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
    
    if exists:
        print(f"      File size: {env_file.stat().st_size} bytes")
        # Store target file for later use
        if is_target:
            target_env_file = env_file
            
        # Show first few lines (mask sensitive data)
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()[:5]
                print(f"      First {len(lines)} lines:")
                for i, line in enumerate(lines, 1):
                    line_clean = line.strip()
                    # Mask sensitive values
                    if any(sensitive in line_clean for sensitive in ['API_KEY', 'SECRET_KEY', 'PASSWORD']):
                        if '=' in line_clean:
                            key, value = line_clean.split('=', 1)
                            if len(value) > 8:
                                masked_value = f"{value[:4]}...{value[-4:]}"
                            else:
                                masked_value = "***"
                            line_clean = f"{key}={masked_value}"
                    print(f"        {i}: {line_clean}")
        except Exception as e:
            print(f"      Error reading: {e}")

print(f"\n🔧 CURRENT ENVIRONMENT VARIABLES:")
relevant_vars = ['ENVIRONMENT', 'OPENROUTER_API_KEY', 'SECRET_KEY', 'DEBUG', 'DATABASE_PATH']
for var in relevant_vars:
    value = os.getenv(var, 'NOT SET')
    if var in ['OPENROUTER_API_KEY', 'SECRET_KEY'] and value != 'NOT SET':
        # Mask sensitive values
        masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        print(f"  {var}: {masked}")
    else:
        print(f"  {var}: {value}")

print(f"\n⚙️ TESTING PYDANTIC SETTINGS FOR {target_env.upper()}:")
try:
    from src.core.config import Settings, get_settings
    print("✅ Successfully imported Settings classes")
    
    # Test 1: Using get_settings() function (recommended)
    print(f"\n1️⃣ Testing get_settings() function:")
    try:
        settings_from_func = get_settings()
        print(f"   Environment: {settings_from_func.ENVIRONMENT}")
        print(f"   OPENROUTER_API_KEY set: {'YES' if settings_from_func.OPENROUTER_API_KEY else 'NO'}")
        print(f"   SECRET_KEY set: {'YES' if settings_from_func.SECRET_KEY else 'NO'}")
        print(f"   Database path: {settings_from_func.DATABASE_PATH}")
    except Exception as e:
        print(f"   ❌ Error with get_settings(): {e}")
    
    # Test 2: Direct Settings instantiation
    print(f"\n2️⃣ Testing direct Settings() instantiation:")
    try:
        settings_direct = Settings()
        print(f"   Environment: {settings_direct.ENVIRONMENT}")
        print(f"   OPENROUTER_API_KEY set: {'YES' if settings_direct.OPENROUTER_API_KEY else 'NO'}")
    except Exception as e:
        print(f"   ❌ Error with direct Settings(): {e}")
    
    # Test 3: Settings with explicit env file
    if target_env_file and target_env_file.exists():
        print(f"\n3️⃣ Testing Settings with explicit env file:")
        try:
            settings_explicit = Settings(_env_file=str(target_env_file))
            print(f"   Environment: {settings_explicit.ENVIRONMENT}")
            print(f"   OPENROUTER_API_KEY set: {'YES' if settings_explicit.OPENROUTER_API_KEY else 'NO'}")
            print(f"   SECRET_KEY set: {'YES' if settings_explicit.SECRET_KEY else 'NO'}")
        except Exception as e:
            print(f"   ❌ Error with explicit env file: {e}")
    else:
        print(f"\n3️⃣ Skipping explicit env file test - target file not found")
    
    # Test 4: Manual dotenv loading
    print(f"\n4️⃣ Testing manual dotenv loading:")
    try:
        from dotenv import load_dotenv
        
        # Clear existing env vars to test loading
        original_api_key = os.getenv('OPENROUTER_API_KEY')
        if 'OPENROUTER_API_KEY' in os.environ:
            del os.environ['OPENROUTER_API_KEY']
        
        print(f"   Before load_dotenv - OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
        
        if target_env_file:
            loaded = load_dotenv(target_env_file, override=True)
            print(f"   load_dotenv({target_env_file.name}) returned: {loaded}")
        else:
            print(f"   No target env file to load")
            loaded = False
        
        print(f"   After load_dotenv - OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
        
        if loaded:
            settings_after_dotenv = Settings()
            print(f"   Settings after manual load - OPENROUTER_API_KEY: {'YES' if settings_after_dotenv.OPENROUTER_API_KEY else 'NO'}")
        
        # Restore original value
        if original_api_key:
            os.environ['OPENROUTER_API_KEY'] = original_api_key
            
    except ImportError:
        print("   python-dotenv not available - install with: pip install python-dotenv")
    except Exception as e:
        print(f"   Error with manual dotenv: {e}")

except Exception as e:
    print(f"❌ Critical Error importing config: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🚀 NEXT STEPS:")
if target_env == "production":
    print("1. Ensure .env.production exists with all required variables")
    print("2. Set ENVIRONMENT=production before running your app:")
    print("   export ENVIRONMENT=production")
    print("   python main.py")
else:
    print(f"1. Ensure .env file exists for {target_env} environment")
    print(f"2. Set ENVIRONMENT={target_env} before running your app")

print("\n💡 USAGE:")
print("python debug_config.py                    # Test production (default)")
print("python debug_config.py development       # Test development")
print("python debug_config.py testing          # Test testing")
#!/usr/bin/env python3
"""
Setup script for Elder Scrolls Lore Bot
This script helps users set up the bot with proper configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping .env file creation")
            return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("   Please edit .env file with your configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def validate_configuration():
    """Validate the current configuration"""
    print("🔧 Validating configuration...")
    
    try:
        from config import Config
        
        config_errors = Config.validate_config()
        
        if not config_errors:
            print("✅ Configuration is valid")
            return True
        else:
            print("❌ Configuration errors found:")
            for error in config_errors:
                print(f"   - {error}")
            print("\n   Please fix these issues in your .env file")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print("   Test output:")
            print(result.stdout)
            if result.stderr:
                print("   Errors:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit the .env file with your configuration:")
    print("   - Add your Telegram bot token")
    print("   - Configure your preferred LLM backend")
    print("   - Set API keys if needed")
    print("\n2. Start the bot:")
    print("   python telegram_bot.py")
    print("\n3. Test the bot:")
    print("   python test_bot.py")
    print("\nFor help, see the README.md file")
    print("\nHappy exploring, traveler! 🗡️⚔️")

def main():
    """Main setup function"""
    print("🚀 Elder Scrolls Lore Bot Setup")
    print("="*40)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Create Environment File", create_env_file),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("   Please fix the issue and run setup again")
            return False
    
    print("\n" + "="*40)
    print("Configuration")
    print("="*40)
    print("\nBefore continuing, please:")
    print("1. Edit the .env file with your configuration")
    print("2. Add your Telegram bot token")
    print("3. Configure your LLM backend")
    
    response = input("\nPress Enter when you've configured the .env file, or 'q' to quit: ")
    if response.lower() == 'q':
        print("Setup cancelled")
        return False
    
    # Validate configuration
    if not validate_configuration():
        print("\n❌ Configuration validation failed")
        print("   Please fix the issues and run setup again")
        return False
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Some tests failed, but setup can continue")
        print("   You may need to fix configuration issues")
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Setup script for Elder Scrolls Lore Bot
Helps users install dependencies and configure the bot
"""

import os
import sys
import subprocess
import shutil

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
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment file"""
    print("\n⚙️  Setting up environment configuration...")
    
    env_file = ".env"
    env_example = ".env.example"
    
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists")
        overwrite = input("   Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("   Skipping environment setup")
            return True
    
    if not os.path.exists(env_example):
        print(f"❌ {env_example} not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print(f"✅ Created {env_file} from template")
        print("   Please edit .env with your configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit .env file with your configuration:")
    print("   - Add your Telegram bot token")
    print("   - Choose and configure your LLM backend")
    print("\n2. Test your setup:")
    print("   python test_bot.py")
    print("\n3. Start the bot:")
    print("   python telegram_bot.py")
    print("\nFor detailed instructions, see README.md")

def main():
    """Main setup function"""
    print("🚀 Elder Scrolls Lore Bot Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
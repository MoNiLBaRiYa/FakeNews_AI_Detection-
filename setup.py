"""Setup script for Fake News Detection System."""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Check if Python version is compatible."""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_mongodb():
    """Check if MongoDB is installed and running."""
    print_header("Checking MongoDB")
    
    try:
        # Try to connect to MongoDB
        from pymongo import MongoClient
        client = MongoClient('mongodb://127.0.0.1:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB is running")
        return True
    except Exception as e:
        print("❌ MongoDB is not running or not installed")
        print(f"Error: {e}")
        print("\nPlease install MongoDB from: https://www.mongodb.com/try/download/community")
        return False

def create_virtual_environment():
    """Create virtual environment."""
    print_header("Creating Virtual Environment")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("Do you want to recreate it? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(venv_path)
        else:
            print("✅ Using existing virtual environment")
            return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")
    
    # Determine pip path
    if sys.platform == "win32":
        pip_path = Path("venv/Scripts/pip.exe")
    else:
        pip_path = Path("venv/bin/pip")
    
    if not pip_path.exists():
        print("❌ Virtual environment not found. Please run setup again.")
        return False
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment variables."""
    print_header("Setting Up Environment Variables")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/n): ")
        if response.lower() != 'y':
            print("✅ Using existing .env file")
            return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ .env file created from template")
        print("\n⚠️  IMPORTANT: Edit .env file and add your API keys!")
        print("   - NEWSAPI_KEY: Get from https://newsapi.org/register")
        print("   - NEWSDATA_KEY: Get from https://newsdata.io/register")
        print("   - SECRET_KEY: Generate a strong random key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_model():
    """Check if ML model exists."""
    print_header("Checking ML Model")
    
    model_path = Path("Model/model.pkl")
    if model_path.exists():
        print("✅ ML model found")
        return True
    else:
        print("⚠️  ML model not found")
        print("   The model should be trained using Model/Final_model_trained.ipynb")
        print("   Or download the pre-trained model if available")
        return False

def create_directories():
    """Create necessary directories."""
    print_header("Creating Directories")
    
    directories = ["logs", "tests"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"✅ Created {directory}/ directory")
        else:
            print(f"✓  {directory}/ directory exists")
    
    return True

def print_next_steps():
    """Print next steps for user."""
    print_header("Setup Complete!")
    
    print("Next steps:")
    print("\n1. Edit .env file with your configuration:")
    print("   - Add API keys (NEWSAPI_KEY, NEWSDATA_KEY)")
    print("   - Set SECRET_KEY to a strong random value")
    
    print("\n2. Ensure MongoDB is running:")
    if sys.platform == "win32":
        print("   net start MongoDB")
    else:
        print("   sudo systemctl start mongod")
    
    print("\n3. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n4. Run the application:")
    print("   cd Backend")
    print("   python app.py")
    
    print("\n5. Open browser:")
    print("   http://localhost:5000")
    
    print("\n6. Run tests (optional):")
    print("   pytest tests/")
    
    print("\n" + "="*60)
    print("For more information, see README.md")
    print("="*60 + "\n")

def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("  Fake News Detection System - Setup")
    print("="*60)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Run setup steps
    steps = [
        ("Python Version", check_python_version),
        ("MongoDB", check_mongodb),
        ("Virtual Environment", create_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Environment Variables", setup_environment),
        ("Directories", create_directories),
        ("ML Model", check_model),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    # Print summary
    print_header("Setup Summary")
    for step_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {step_name}")
    
    # Check if all critical steps passed
    critical_steps = ["Python Version", "Virtual Environment", "Dependencies"]
    all_critical_passed = all(
        result for step_name, result in results 
        if step_name in critical_steps
    )
    
    if all_critical_passed:
        print_next_steps()
    else:
        print("\n❌ Setup failed. Please fix the errors above and run setup again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

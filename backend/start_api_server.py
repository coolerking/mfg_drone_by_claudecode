#!/usr/bin/env python3
"""
API Server Startup Script
Start the MFG Drone Backend API Server
"""

import sys
import os
import subprocess

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'numpy',
        'scipy',
        'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server"""
    try:
        import uvicorn
        from api_server.main import app
        
        print(f"Starting MFG Drone Backend API Server...")
        print(f"Server will be available at: http://{host}:{port}")
        print(f"API documentation: http://{host}:{port}/docs")
        print(f"OpenAPI spec: http://{host}:{port}/openapi.json")
        print()
        
        uvicorn.run(
            "api_server.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        print("Please install dependencies first: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"Failed to start server: {e}")
        return False

def main():
    """Main function"""
    print("=== MFG Drone Backend API Server ===\n")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install dependencies first:")
        print("  pip install -r requirements.txt")
        print()
        
        response = input("Would you like to install dependencies now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_dependencies():
                sys.exit(1)
        else:
            print("Cannot start server without dependencies.")
            sys.exit(1)
    
    # Start server
    print("All dependencies are available.")
    print("Starting API server...")
    print()
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
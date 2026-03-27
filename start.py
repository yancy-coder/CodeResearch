#!/usr/bin/env python3
"""CoderResearch Full-Stack Startup Script - v3.0"""
import subprocess
import sys
import os
import time
import platform


def check_dependency(module_name):
    """检查 Python 依赖是否已安装"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def start_backend():
    """Start FastAPI backend"""
    print("[BACKEND] Starting FastAPI service...")
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    
    # Check dependencies
    if not check_dependency("fastapi"):
        print("[BACKEND] Installing dependencies...")
        req_file = os.path.join(backend_dir, "requirements.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
    
    # Start service
    is_windows = platform.system() == "Windows"
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=backend_dir,
        shell=is_windows,
        creationflags=subprocess.CREATE_NEW_CONSOLE if is_windows else 0
    )
    return proc


def start_frontend():
    """Start frontend dev server"""
    print("[FRONTEND] Starting Vite + React service...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    
    # Check node_modules
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("[FRONTEND] Installing dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, shell=True)
    
    # Start service
    is_windows = platform.system() == "Windows"
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=frontend_dir,
        shell=is_windows,
        creationflags=subprocess.CREATE_NEW_CONSOLE if is_windows else 0
    )
    return proc


def main():
    print("=" * 60)
    print("  CoderResearch v3.0 - Full-Stack Mode")
    print("=" * 60)
    print()
    
    backend_proc = None
    frontend_proc = None
    
    try:
        backend_proc = start_backend()
        time.sleep(3)  # Wait for backend to initialize
        
        frontend_proc = start_frontend()
        time.sleep(3)  # Wait for frontend to initialize
        
        print()
        print("Services started successfully:")
        print("   Frontend: http://localhost:5173")
        print("   API:      http://localhost:8000")
        print("   Docs:     http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop")
        print()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        
        if backend_proc:
            backend_proc.terminate()
            backend_proc.wait()
            print("   [BACKEND] Stopped")
        
        if frontend_proc:
            frontend_proc.terminate()
            frontend_proc.wait()
            print("   [FRONTEND] Stopped")
        
        print("\nGoodbye!")


if __name__ == "__main__":
    main()

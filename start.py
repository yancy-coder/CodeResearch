#!/usr/bin/env python3
"""CoderResearch Full-Stack Startup Script - v3.0"""
import subprocess
import sys
import os
import time


def start_backend():
    """Start FastAPI backend"""
    print("[BACKEND] Starting FastAPI service...")
    os.chdir("backend")
    
    # Check dependencies
    try:
        import fastapi
    except ImportError:
        print("[BACKEND] Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Start service
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    os.chdir("..")
    return proc


def start_frontend():
    """Start frontend dev server"""
    print("[FRONTEND] Starting Vite + React service...")
    os.chdir("frontend")
    
    # Check node_modules
    if not os.path.exists("node_modules"):
        print("[FRONTEND] Installing dependencies...")
        subprocess.run(["npm", "install"], check=True)
    
    # Start service
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    os.chdir("..")
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
        time.sleep(2)  # Wait for backend
        
        frontend_proc = start_frontend()
        time.sleep(2)  # Wait for frontend
        
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
            print("   [BACKEND] Stopped")
        
        if frontend_proc:
            frontend_proc.terminate()
            print("   [FRONTEND] Stopped")
        
        print("\nGoodbye!")


if __name__ == "__main__":
    main()

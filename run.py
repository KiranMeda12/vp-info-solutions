"""
VP Info Solutions Pvt Ltd - Antigravity Lead Management System
Application Launcher Script
Runs FastAPI Backend and Streamlit Frontend
"""

import sys
import time
import subprocess
import argparse
import webbrowser

def start_backend():
    print("Starting FastAPI Backend on http://127.0.0.1:8000...")
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(cmd)

def start_frontend():
    print("Starting Streamlit Frontend on http://127.0.0.1:8501...")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    return subprocess.Popen(cmd)

def main():
    parser = argparse.ArgumentParser(description="Antigravity Application Runner")
    parser.add_argument("--backend-only", action="store_true", help="Start only the FastAPI backend")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the Streamlit frontend")
    args = parser.parse_args()

    procs = []
    try:
        if args.backend_only:
            p_back = start_backend()
            procs.append(p_back)
            p_back.wait()
        elif args.frontend_only:
            p_front = start_frontend()
            procs.append(p_front)
            p_front.wait()
        else:
            # Start both
            p_back = start_backend()
            procs.append(p_back)
            
            # Wait 2 seconds for backend to initialize
            time.sleep(2)
            
            p_front = start_frontend()
            procs.append(p_front)

            print("\n" + "="*60)
            print("[ONLINE] VP Info Solutions Pvt Ltd Portal is running!")
            print("Frontend URL: http://localhost:8501")
            print("Backend API & Swagger: http://localhost:8000/docs")
            print("Power BI Feed: http://localhost:8000/api/export/powerbi?format=json")
            print("="*60 + "\n")

            p_front.wait()
            p_back.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        for p in procs:
            p.terminate()

if __name__ == "__main__":
    main()

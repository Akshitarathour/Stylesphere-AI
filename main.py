import os
import sys
import subprocess

def main():
    print("=" * 50)
    print("          StyleSphere AI - Cognitive Wardrobe")
    print("=" * 50)
    
    # Initialize the database schema
    try:
        import database
        database.init_db()
        print("[OK] Database initialized successfully (stylesphere.db).")
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        sys.exit(1)
        
    # Check if streamlit is installed
    try:
        import streamlit
        print("[OK] Streamlit is installed.")
    except ImportError:
        print("[INFO] Streamlit is not installed. Installing requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        except Exception as e:
            print(f"[ERROR] Failed to install requirements: {e}")
            sys.exit(1)
            
    # Launch app.py using streamlit
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    print(f"[*] Starting the Streamlit application: py -m streamlit run {app_path}")
    
    try:
        # Run streamlit in a sub-process using sys.executable
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
    except KeyboardInterrupt:
        print("\n[*] StyleSphere AI stopped by user.")
    except Exception as e:
        print(f"[ERROR] Error launching Streamlit: {e}")
        print("Please try running: streamlit run app.py")

if __name__ == "__main__":
    main()

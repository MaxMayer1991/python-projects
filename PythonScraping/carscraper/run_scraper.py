import subprocess
import sys
import datetime
import os
def run_spider(spider_name="carspider"):
    """Start Scrapy spider by subprocess"""
    # Generate timestamp for unique files
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Determine correct path to Python
    if os.name == 'nt':  # Windows
        # Trying to find venv in different directories
        possible_paths = [
            os.path.join('.venv', 'Scripts', 'python.exe'),
            os.path.join('..', '.venv', 'Scripts', 'python.exe'),
            os.path.join('venv', 'Scripts', 'python.exe'),
            sys.executable  # Fallback - current Python
        ]
        python_exec = None
        for path in possible_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                python_exec = full_path
                break
        if not python_exec:
            python_exec = sys.executable
            print(f"⚠️  Using system Python: {python_exec}")
        else:
            print(f"✅ Found Python: {python_exec}")
    else:
        python_exec = sys.executable
    # Check that we are in the correct directory (it should be scrapy.cfg)
    scrapy_cfg = 'scrapy.cfg'
    if not os.path.exists(scrapy_cfg):
        print(f"❌ scrapy.cfg not found in{os.path.abspath('carscraper')}")
        print("Run the script from the project root directory!")
        return False
    # Create the required folders
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    # Change the working directory to carscraper (where scrapy.cfg is located)
    original_dir = os.getcwd()
    scrapy_dir = os.path.abspath('carscraper')
    os.chdir(scrapy_dir)
    try:
        # Generating command for start spider
        log_file = os.path.join('..', 'logs', f'spider_{timestamp}.log')
        data_file = os.path.join('..', 'data', f'cars_{timestamp}.csv')
        cmd = [
            python_exec, '-m', 'scrapy', 'crawl', spider_name,
            '-L', 'INFO',
            '--logfile', log_file,
            '-o', data_file
        ]
        print(f"🚀 Start command: {' '.join(cmd)}")
        print(f"📁 Working folder: {os.getcwd()}")
        # Start spider
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=scrapy_dir
        )
        print(f"✅ Spider '{spider_name}' ended successfully (code: {result.returncode})")
        print(f"📄 Log file: {os.path.abspath(log_file)}")
        print(f"📊 Data file: {os.path.abspath(data_file)}")

        if result.stdout:
            print("📤 Stdout:", result.stdout[:500])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Start error spider: {e}")
        print(f"📤 Stdout: {e.stdout}")
        print(f"📥 Stderr: {e.stderr}")
        return False
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print(f"🔍 Check path to Python: {python_exec}")
        return False
    finally:
        # Return to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run scrapy spider from CLI")
    parser.add_argument('--spider', default="carspider", help='Spider name to run')
    args = parser.parse_args()
    success = run_spider(args.spider)
    sys.exit(0 if success else 1)
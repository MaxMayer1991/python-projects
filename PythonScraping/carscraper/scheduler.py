import os
import sys
import subprocess
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

def is_docker_environment():
    """Automatically determine if we are running in Docker"""
    return (os.path.exists('/.dockerenv') or
            os.getenv('DOCKER_ENV') == 'true' or
            os.path.exists('/app/carscraper'))
# Auto determine environment
if is_docker_environment():
    print("🐳 Docker environment found")
    CARSCRAPER_DIR = '/app'
    DUMP_DIR = '/app/data'
    LOG_DIR = '/app/logs'
    DEFAULT_DB_HOST = 'postgres'
else:
    print("💻 Local environment found")
    current_dir = os.getcwd()
    if os.path.exists('carscraper') and os.path.exists('carscraper/scrapy.cfg'):
        CARSCRAPER_DIR = os.path.abspath('carscraper')
        project_root = current_dir
    else:
        project_root = os.path.dirname(current_dir)
        CARSCRAPER_DIR = current_dir
    DUMP_DIR = os.path.join(project_root, 'data')
    LOG_DIR = os.path.join(project_root, 'logs')
    DEFAULT_DB_HOST = 'localhost'
# ✅ SECURE getting environment variables (WITHOUT variables by default!)
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST', DEFAULT_DB_HOST)
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
# Check required variables
required_vars = {
    'POSTGRES_DB': DB_NAME,
    'POSTGRES_USER': DB_USER,
    'POSTGRES_PASSWORD': DB_PASS
}
missing_vars = [name for name, value in required_vars.items() if not value]
if missing_vars:
    print(f"❌ CRITICAL ERROR: Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("🔧 Set them in .env file or in docker-compose file")
    sys.exit(1)
# Scheduler time
SPIDER_TIME = os.getenv('SPIDER_TIME')
DUMP_TIME = os.getenv('DUMP_TIME')
# Creating directories
for directory in [DUMP_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

def run_spider():
    """Launch Scrapy spider"""
    print(f"[{datetime.now()}] 🕷️ Launching Scrapy spider...")
    original_dir = os.getcwd()
    try:
        os.chdir(CARSCRAPER_DIR)
        if not os.path.exists('scrapy.cfg'):
            raise FileNotFoundError(f"scrapy.cfg not found in {CARSCRAPER_DIR}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"{LOG_DIR}/spider_{timestamp}.log"
        data_file = f"{DUMP_DIR}/cars_{timestamp}.csv"
        cmd = [
            sys.executable, '-m', 'scrapy', 'crawl', 'carspider',
            '-L', 'INFO',
            '--logfile', log_file,
            '-o', data_file
        ]
        print(f"📋 Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Spider successfully ended")
        print(f"📄 Logs: {log_file}")
        print(f"📊 Data: {data_file}")
    except Exception as e:
        print(f"❌ Error spider: {e}")
    finally:
        os.chdir(original_dir)

def dump_db():
    """Creating a database dump"""
    print(f"[{datetime.now()}] 💾 Creating a database dump...")
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    dump_file = os.path.join(DUMP_DIR, f'dump_{timestamp}.sql')
    cmd = ['pg_dump', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, '-d', DB_NAME, '-f', dump_file]
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASS
    try:
        subprocess.run(cmd, env=env, check=True)
        print(f"✅ Dump created: {dump_file}")
    except Exception as e:
        print(f"❌ Dump error: {e}")

def main():
    """Main function"""
    print("🚀 Starting the scheduler...")
    print(f"📁 Scrapy: {CARSCRAPER_DIR}")
    print(f"📁 Logs: {LOG_DIR}")
    print(f"📁 Data: {DUMP_DIR}")
    print(f"🔗 DB: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    scheduler = BlockingScheduler()
    # Task planning
    hour, minute = map(int, SPIDER_TIME.split(':'))
    scheduler.add_job(run_spider, 'cron', hour=hour, minute=minute, id='spider_job')
    print(f"⏰ Spider: {SPIDER_TIME}")

    d_hour, d_minute = map(int, DUMP_TIME.split(':'))
    scheduler.add_job(dump_db, 'cron', hour=d_hour, minute=d_minute, id='dump_job')
    print(f"💾 Dump: {DUMP_TIME}")
    # Test launch
    if os.getenv('RUN_SPIDER_NOW', '').lower() == 'true':
        print("🧪 Test run...")
        run_spider()
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("🛑 Stopped")

if __name__ == '__main__':
    main()


def run_spider():
    """Launch Scrapy spider"""
    print(f"[{datetime.now()}] 🕷️ Launching Scrapy spider...")
    original_dir = os.getcwd()

    try:
        os.chdir(CARSCRAPER_DIR)
        if not os.path.exists('scrapy.cfg'):
            raise FileNotFoundError(f"scrapy.cfg not found in {CARSCRAPER_DIR}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"{LOG_DIR}/spider_{timestamp}.log"
        data_file = f"{DUMP_DIR}/cars_{timestamp}.csv"
        cmd = [
            sys.executable, '-m', 'scrapy', 'crawl', 'carspider',
            '-L', 'INFO',
            '--logfile', log_file,
            '-o', data_file
        ]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Spider completed successfully")
        print(f"📄 Log: {log_file}")
        print(f"📊 Data: {data_file}")

    except Exception as e:
        print(f"❌ Spider error: {e}")
    finally:
        os.chdir(original_dir)
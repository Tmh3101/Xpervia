import time
import schedule
import traceback
from datetime import datetime
from app.rag.indexing.upsert import embed_all_courses

RUN_INTERVAL_HOURS = 4   # 4 tiếng/lần
LOG_FILE = "logs/cron_embed.log"  # lưu log tại /chatbot_service/logs/

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def job():
    log("Starting scheduled job: embed_all_courses()")
    try:
        embed_all_courses()
        log("Finished embed_all_courses() successfully.")
    except Exception as e:
        err = traceback.format_exc()
        log(f"Error during embed_all_courses(): {e}\n{err}")

if __name__ == "__main__":
    log(f"Embedding CRON started — running every {RUN_INTERVAL_HOURS}h")
    schedule.every(RUN_INTERVAL_HOURS).hours.do(job)

    job()

    while True:
        schedule.run_pending()
        time.sleep(60)

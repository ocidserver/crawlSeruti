import os
import sys
import pathlib
import random
from datetime import datetime, timedelta

# Ensure project root is on sys.path for 'app' package imports
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import db
from app.config import Config


def main():
    job_name = 'SMOKE_SERUTI'
    start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Ensure job exists
    if not db.get_job_by_name(job_name):
        db.add_job({
            'id': f'{job_name}_{int(datetime.now().timestamp())}',
            'name': job_name,
            'crawler_type': 'seruti',
            'start_date': start_date,
            'end_date': end_date,
            'hour': 9,
            'minute': 5,
            'created_at': datetime.now().isoformat()
        })

    # Seed 7 days of logs, and create simple CSV files
    dl_dir = Config.DOWNLOAD_PATH
    os.makedirs(dl_dir, exist_ok=True)

    for i in range(7):
        day = (datetime.now() - timedelta(days=6 - i))
        data_date = day.strftime('%Y-%m-%d')
        filename = f'smoke_{data_date}.csv'
        dl_path = os.path.join(dl_dir, filename)
        if not os.path.exists(dl_path):
            with open(dl_path, 'w', encoding='utf-8') as f:
                f.write('col1,col2\n')
                for r in range(random.randint(1, 5)):
                    f.write(f'{r},{data_date}\n')
        db.add_download_log(
            nama_file=filename,
            tanggal_download=day.strftime('%Y-%m-%d %H:%M:%S'),
            laman_web='SerutiCrawler',
            data_tanggal=data_date,
            task_name=job_name
        )

    print(f'Inserted synthetic job/logs for smoke test: {job_name} {start_date} -> {end_date}')


if __name__ == '__main__':
    main()

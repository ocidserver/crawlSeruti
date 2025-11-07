import unittest
import sys
import pathlib
from flask import session

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.database import db


class DashboardReportSmokeTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        # Login session bypass
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['full_name'] = 'Administrator'
            sess['role'] = 'admin'

    def test_dashboard_metrics_and_report(self):
        # Seed ensures SMOKE_SERUTI exists with last 7 days
        job = db.get_job_by_name('SMOKE_SERUTI')
        self.assertIsNotNone(job, 'Seed job SMOKE_SERUTI not found. Run scripts/smoke_seed.py first')

        # Metrics
        qs = f"task=SMOKE_SERUTI&start_date={job['start_date']}&end_date={job['end_date']}"
        r = self.client.get(f"/dashboard/api/metrics?{qs}")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['total_logs'], 7)

        # Report generation (Seruti)
        r2 = self.client.post('/report/run', json={
            'task_name': 'SMOKE_SERUTI',
            'generator': 'seruti',
            'start_date': job['start_date'],
            'end_date': job['end_date']
        })
        self.assertEqual(r2.status_code, 200)
        self.assertIn('Content-Disposition', r2.headers)

        # Report history page loads
        r3 = self.client.get('/report/history')
        self.assertEqual(r3.status_code, 200)

        # Dashboard page loads
        r4 = self.client.get('/dashboard/')
        self.assertEqual(r4.status_code, 200)


if __name__ == '__main__':
    unittest.main()

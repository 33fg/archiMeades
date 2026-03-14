#!/usr/bin/env python3
"""Test Celery task submission - diagnose why jobs stay pending."""

import os
import sys
import time

# Ensure backend is on path and we use project venv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

def main():
    from app.celery_app import app
    from app.tasks.mcmc import run_mcmc_task
    from app.core.config import settings

    print("Broker:", settings.redis_url)
    print("DGX_CELERY_QUEUE:", repr(settings.dgx_celery_queue))
    print()

    # Use a fake job_id - task will fail "Job not found" but we'll see if it gets picked up
    fake_job_id = "test-diagnostic-001"
    print("Submitting run_mcmc_task with job_id:", fake_job_id)

    result = run_mcmc_task.apply_async(
        args=[fake_job_id],
        queue="celery",
    )
    task_id = result.id
    print("Task ID:", task_id)
    print()

    for i in range(15):
        print(f"[{i}s] Checking...")
        inspect = app.control.inspect()
        active = inspect.active() or {}
        reserved = inspect.reserved() or {}
        for worker, tasks in active.items():
            for t in tasks:
                if t.get("id") == task_id:
                    print(f"  -> ACTIVE on {worker}")
        for worker, tasks in reserved.items():
            for t in tasks:
                if t.get("id") == task_id:
                    print(f"  -> RESERVED on {worker}")
        try:
            r = result.get(timeout=2)
            print("  -> Result:", r)
            break
        except Exception as e:
            pass
        time.sleep(1)

    print()
    print("Done. If you saw RESERVED/ACTIVE, worker is picking up tasks.")
    print("If nothing, worker may not be connected or not consuming 'celery' queue.")

if __name__ == "__main__":
    main()

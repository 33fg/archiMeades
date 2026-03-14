#!/usr/bin/env python3
"""Test if Celery worker picks up simulation tasks."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

def main():
    from app.celery_app import app
    from app.tasks.simulation import run_simulation_task
    from app.core.config import settings

    print("=== Celery connectivity test ===\n")
    print("Redis URL:", settings.redis_url)
    print("Default queue:", settings.celery_queue)
    print("DGX queue:", settings.dgx_celery_queue or "(not set)")
    print()

    # 1. Ping workers
    print("1. Pinging workers...")
    try:
        ping = app.control.ping(timeout=3)
        if isinstance(ping, list):
            ping = ping[0] if ping else {}
        elif not isinstance(ping, dict):
            ping = {}
        if ping:
            for worker, pong in ping.items():
                print(f"   OK: {worker} responded")
        else:
            print("   NO WORKERS RESPONDING - Celery worker is not running!")
            print("   Run: npm run celery:worker")
            sys.exit(1)
    except Exception as e:
        print(f"   FAILED: {e}")
        print("   Is Redis running? Is a Celery worker running?")
        sys.exit(1)

    # 2. Submit a simulation task (fake ID - will fail but proves worker picks it up)
    print("\n2. Submitting simulation task (fake ID - will fail with 'not found')...")
    result = run_simulation_task.apply_async(args=["00000000-0000-0000-0000-000000000000"])
    task_id = result.id
    print(f"   Task ID: {task_id}")

    # 3. Wait for result (should fail quickly)
    for i in range(10):
        time.sleep(1)
        try:
            r = result.get(timeout=2)
            print(f"\n   Task completed in {i+1}s. Result: {r}")
            if "error" in r or "not found" in str(r).lower():
                print("   (Expected failure - fake ID. Worker IS processing tasks.)")
            sys.exit(0)
        except Exception:
            pass
        print(f"   [{i+1}s] waiting...")

    print("\n   Timeout - task was not picked up. Worker may not be consuming the simulation queue.")
    sys.exit(1)

if __name__ == "__main__":
    main()

import asyncio
import aiohttp
import sqlite3
import uuid
import json
from datetime import datetime
from database import DB_PATH
from agent import evaluate_event  # Import the deterministic orchestrator core

# Target API for tracking live exchange rate data
API_URL = "https://api.frankfurter.app/latest?from=USD&to=EUR"
POLL_INTERVAL = 5  # Seconds between API polls

async def fetch_rate(session):
    """Asynchronously fetches the latest exchange rate from the public API."""
    try:
        async with session.get(API_URL) as response:
            if response.status == 200:
                return await response.json()
    except Exception as e:
        print(f"[-] Error fetching data: {e}")
    return None

def log_event_to_db(event_id, source, metric, baseline, observed, variance, raw_payload):
    """Inserts a detected data anomaly breach into the SQLite ledger."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO data_events (event_id, source_api, metric_name, baseline_value, observed_value, variance_percentage, raw_payload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (event_id, source, metric, baseline, observed, variance, json.dumps(raw_payload)))
        conn.commit()
        print(f"[+] Event logged to database: {event_id} (Variance: {variance:.4f}%)")
    except Exception as e:
        print(f"[-] Database error while logging event: {e}")
    finally:
        conn.close()

async def watch_stream():
    """Continuous background loop monitoring data streams and pushing updates every tick."""
    print(f"[*] Starting Watcher Engine. Monitoring {API_URL} every {POLL_INTERVAL}s...")
    baseline_rate = None
    
    async with aiohttp.ClientSession() as session:
        while True:
            data = await fetch_rate(session)
            if data and "rates" in data:
                current_rate = data["rates"]["EUR"]
                
                # Establish initial baseline on the very first pull
                if baseline_rate is None:
                    baseline_rate = current_rate
                    print(f"[*] Baseline established for USD/EUR: {baseline_rate}")
                else:
                    # Calculate percentage variance
                    variance = abs((current_rate - baseline_rate) / baseline_rate) * 100
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Rate: {current_rate:.4f} | Var: {variance:.4f}%")
                    
                    # Force data pipeline generation on every loop iteration
                    event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
                    print(f"[!] Logging loop cycle tick...")
                    
                    # 1. Archive the details to the data_events table
                    log_event_to_db(
                        event_id=event_id,
                        source="Frankfurter API",
                        metric="USD_EUR_Rate",
                        baseline=baseline_rate,
                        observed=current_rate,
                        variance=variance,
                        raw_payload=data
                    )
                    
                    # 2. Handover event directly to our Orchestrator Router for action assignment
                    evaluate_event(event_id, "USD_EUR_Rate", variance)
                    
                    # Dynamically adjust baseline to the new normal
                    baseline_rate = current_rate
                    print("-" * 60)
                        
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(watch_stream())
    except KeyboardInterrupt:
        print("\n[*] Watcher engine stopped gracefully.")
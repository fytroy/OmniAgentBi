import sqlite3
import os
from datetime import datetime
from database import DB_PATH

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

def send_alert(action_id, event_id):
    """Executes priority alert handling for critical financial events."""
    print(f"[🚨 Skill Executing] Assembling critical operational alert for {event_id}...")
    
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Fetch data about the breach to format the alert body
        cursor.execute('SELECT metric_name, variance_percentage, observed_value FROM data_events WHERE event_id = ?', (event_id,))
        event_data = cursor.fetchone()
        
        if event_data:
            metric, variance, observed = event_data
            
            # Format the alert notification template text payload
            alert_payload = (
                f"=== CRITICAL INCIDENT REPORT ===\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Incident ID: {action_id}\n"
                f"Source Event: {event_id}\n"
                f"Metric Breached: {metric}\n"
                f"Observed Metric Value: {observed:.4f}\n"
                f"Calculated Volatility Variance: {variance:.4f}%\n"
                f"Status: ACTION_REQUIRED - Routed via Autonomous Agent Rule Engine.\n"
                f"================================\n"
            )
            
            # Dispatch action: Write outbound dispatch message body to file log drops
            dispatch_path = os.path.join(LOGS_DIR, f"alert_dispatch_{action_id}.txt")
            with open(dispatch_path, 'w') as alert_file:
                alert_file.write(alert_payload)
            print(f"[🚨 Dispatch Hub] Outbound emergency alert sent -> {dispatch_path}")
            
            # Update database status state
            cursor.execute('''
                UPDATE agent_actions 
                SET execution_status = 'DISPATCHED',
                    action_summary = action_summary || ' [Emergency alert file generated successfully.]'
                WHERE action_id = ?
            ''', (action_id,))
            conn.commit()
            print(f"[🚨 Skill Success] Action {action_id} logged as DISPATCHED.")
            
    except Exception as e:
        print(f"[-] Critical notification dispatch error: {e}")
    finally:
        conn.close()
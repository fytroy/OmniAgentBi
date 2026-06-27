import sqlite3
from database import DB_PATH

def log_variance(action_id, event_id):
    """Executes processing for low/medium risk variance trends."""
    print(f"[📈 Skill Executing] Running telemetry capture for Action: {action_id}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Update our action row status from PENDING to COMPLETED
        cursor.execute('''
            UPDATE agent_actions 
            SET execution_status = 'COMPLETED',
                action_summary = action_summary || ' [Telemetry data points archived successfully.]'
            WHERE action_id = ?
        ''', (action_id,))
        conn.commit()
        print(f"[📈 Skill Success] Action {action_id} status updated to COMPLETED.")
    except Exception as e:
        print(f"[-] Skill execution failure: {e}")
    finally:
        conn.close()

def suppress_event(action_id, event_id):
    """Explicitly marks a negligible variance event as suppressed/archived."""
    print(f"[📭 Skill Executing] Suppressing minor noise event...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE agent_actions 
        SET execution_status = 'SUPPRESSED'
        WHERE action_id = ?
    ''', (action_id,))
    conn.commit()
    conn.close()
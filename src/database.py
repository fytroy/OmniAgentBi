import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'analytics.db')

def init_db():
    """Initializes the local SQLite analytics database and creates required tables."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Table for tracking event anomalies captured by the watcher loop
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_events (
            event_id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source_api TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            baseline_value REAL,
            observed_value REAL,
            variance_percentage REAL,
            raw_payload TEXT NOT NULL
        )
    ''')
    
    # 2. Table for tracking the agent's autonomous routing decisions and actions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_actions (
            action_id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ai_classification TEXT NOT NULL,
            assigned_skill TEXT NOT NULL,
            execution_status TEXT NOT NULL,
            action_summary TEXT,
            FOREIGN KEY (event_id) REFERENCES data_events (event_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(True)

if __name__ == "__main__":
    init_db()
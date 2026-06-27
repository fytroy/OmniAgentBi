import sqlite3
import json
import uuid
import os
from database import DB_PATH

def route_to_skill(event_id, severity, reasoning):
    """
    Parses the deterministic evaluation results, logs the autonomous 
    routing decision, and dynamically executes the assigned functional skill.
    """
    action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
    
    # Map the operational severity to the exact execution path/skill
    if severity in ["CRITICAL", "HIGH"]:
        assigned_skill = "skills.notifier.send_alert"
    elif severity == "MEDIUM":
        assigned_skill = "skills.analyze_market.log_variance"
    else:
        assigned_skill = "skills.analyze_market.suppress_event"
        
    execution_status = "PENDING"

    # Log the operational action directly into the database ledger
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO agent_actions (action_id, event_id, ai_classification, assigned_skill, execution_status, action_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (action_id, event_id, severity, assigned_skill, execution_status, reasoning))
        conn.commit()
        print(f"[⚙️] Orchestrator Decision: Severity [{severity}] -> Routed to [{assigned_skill}]")
        
        # =====================================================================
        # 🔗 DYNAMIC EXECUTION HUB
        # =====================================================================
        if assigned_skill == "skills.notifier.send_alert":
            from skills.notifier import send_alert
            send_alert(action_id, event_id)
            
        elif assigned_skill == "skills.analyze_market.log_variance":
            from skills.analyze_market import log_variance
            log_variance(action_id, event_id)
            
        elif assigned_skill == "skills.analyze_market.suppress_event":
            from skills.analyze_market import suppress_event
            suppress_event(action_id, event_id)
        # =====================================================================
            
    except Exception as e:
        print(f"[-] Database logging or skill execution failure in agent core: {e}")
    finally:
        conn.close()
        
    return assigned_skill, action_id

def evaluate_event(event_id, metric, variance):
    """
    Evaluates the anomaly using production-grade rule engine logic
    instead of an external or cloud LLM.
    """
    print(f"[⚙️] Orchestrator Core parsing event {event_id}...")
    
    # Define enterprise operational risk thresholds
    if variance >= 0.05:
        severity = "CRITICAL"
        reasoning = f"Critical threshold breach detected for {metric}. Variance is at {variance:.4f}%, exceeding safety margins."
    elif variance >= 0.02:
        severity = "HIGH"
        reasoning = f"High variance detected for {metric} at {variance:.4f}%. Requires administrative evaluation."
    elif variance >= 0.005:
        severity = "MEDIUM"
        reasoning = f"Moderate fluctuation noticed for {metric} at {variance:.4f}%. Logging standard variance report."
    else:
        severity = "LOW"
        reasoning = f"Negligible variance observed for {metric} ({variance:.4f}%). Dropping standard telemetry log."

    return route_to_skill(event_id, severity, reasoning)

if __name__ == "__main__":
    print("[*] Local Deterministic Orchestrator compiles perfectly. Ready for execution.")
import streamlit as st
import sqlite3
import pandas as pd
import os

# Identify path to database ledger
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'analytics.db')

def load_data(query):
    """Safely connects to SQLite and reads data into a Pandas DataFrame."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading database records: {e}")
        return pd.DataFrame()

# Configure page visual properties
st.set_page_config(page_title="OmniAgent BI Operational Terminal", layout="wide", page_icon="⚙️")

st.title("⚙️ OmniAgent BI Operational Analytics Terminal")
st.markdown("Real-time telemetry streams, operational metrics, and autonomous routing logs.")
st.divider()

# =====================================================================
# 📈 METRIC CARDS LAYER
# =====================================================================
col1, col2, col3 = st.columns(3)

total_events_df = load_data("SELECT COUNT(*) as count FROM data_events")
total_events = total_events_df['count'].iloc[0] if not total_events_df.empty else 0

total_actions_df = load_data("SELECT COUNT(*) as count FROM agent_actions WHERE execution_status != 'PENDING'")
total_actions = total_actions_df['count'].iloc[0] if not total_actions_df.empty else 0

critical_df = load_data("SELECT COUNT(*) as count FROM agent_actions WHERE ai_classification = 'CRITICAL'")
critical_count = critical_df['count'].iloc[0] if not critical_df.empty else 0

with col1:
    st.metric(label="Total Logged Anomalies", value=total_events)
with col2:
    st.metric(label="Autonomous Actions Executed", value=total_actions)
with col3:
    st.metric(label="Critical Escalations", value=critical_count, delta=f"{critical_count} Alert(s)", delta_color="inverse")

# =====================================================================
# 🗃️ LIVE DATA VIEWERS LAYER
# =====================================================================
st.subheader("📋 Recent Orchestration Logs")

# Join both tables to showcase how the engine maps telemetry to actual business actions
logs_query = """
    SELECT 
        e.event_id as [Event ID],
        e.timestamp as [Timestamp],
        e.metric_name as [Metric Name],
        e.variance_percentage as [Variance %],
        a.ai_classification as [Risk Classification],
        a.assigned_skill as [Executed Skill Path],
        a.execution_status as [Execution Status]
    FROM data_events e
    LEFT JOIN agent_actions a ON e.event_id = a.event_id
    ORDER BY e.timestamp DESC
    LIMIT 10
"""
logs_df = load_data(logs_query)

if not logs_df.empty:
    st.dataframe(logs_df, use_container_width=True)
else:
    st.info("No orchestration telemetry rows found in the database. Run the watcher engine to populate data.")

# =====================================================================
# 📉 VOLATILITY STREAM VISUALIZATION
# =====================================================================
st.subheader("📊 Historical Volatility Trajectory")
chart_query = "SELECT timestamp, observed_value FROM data_events ORDER BY timestamp DESC LIMIT 30"
chart_df = load_data(chart_query)

if not chart_df.empty:
    chart_df['timestamp'] = pd.to_datetime(chart_df['timestamp'])
    chart_df = chart_df.sort_values(by='timestamp')
    st.line_chart(data=chart_df, x='timestamp', y='observed_value', use_container_width=True)

import time
time.sleep(5)      # Wait 5 seconds
st.rerun()
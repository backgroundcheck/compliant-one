# app.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- CONFIG ---
DB_URL = st.secrets["db_url"] if "db_url" in st.secrets else "postgresql://user:password@localhost:5432/compliant"
engine = create_engine(DB_URL)

st.set_page_config(page_title="Compliant.one", layout="wide")
st.title("🛡️ Compliant.one")
st.subheader("Threat & Compliance Intelligence Platform")

tabs = st.tabs(["Entities", "Risk Assessments", "Alerts", "Compliance Checks", "Cases", "OSINT Data"])

# --- ENTITIES TAB ---
with tabs[0]:
    st.header("Entities")
    search = st.text_input("Search for an entity (name, alias, etc.)", "")
    with engine.connect() as conn:
        if search:
            query = text("""
                SELECT id, name, entity_type, risk_level, risk_score, is_active
                FROM public.entities
                WHERE name ILIKE :search OR :search = ANY(aliases)
                ORDER BY risk_score DESC
                LIMIT 20
            """)
            df = pd.read_sql(query, conn, params={"search": f"%{search}%"})
        else:
            query = text("""
                SELECT id, name, entity_type, risk_level, risk_score, is_active
                FROM public.entities
                ORDER BY risk_score DESC
                LIMIT 20
            """)
            df = pd.read_sql(query, conn)
    if df.empty:
        st.info("No entities found.")
    else:
        st.dataframe(df, use_container_width=True)
        selected = st.selectbox("Select an entity for details", df["name"].tolist())
        entity_id = df[df["name"] == selected]["id"].values[0]
        with engine.connect() as conn:
            risk_df = pd.read_sql(
                text("SELECT risk_score, risk_level, assessment_date, factors FROM public.risk_assessments WHERE entity_id = :eid ORDER BY assessment_date DESC LIMIT 5"),
                conn, params={"eid": entity_id}
            )
            alert_df = pd.read_sql(
                text("SELECT title, severity, status, created_at FROM public.alerts WHERE entity_id = :eid ORDER BY created_at DESC LIMIT 10"),
                conn, params={"eid": entity_id}
            )
            comp_df = pd.read_sql(
                text("SELECT check_type, status, checked_at, results FROM public.compliance_checks WHERE entity_id = :eid ORDER BY checked_at DESC LIMIT 5"),
                conn, params={"eid": entity_id}
            )
            case_df = pd.read_sql(
                text("""SELECT c.title, c.status, c.priority, c.created_at
                         FROM public.cases c
                         JOIN public.case_entities ce ON ce.case_id = c.id
                         WHERE ce.entity_id = :eid
                         ORDER BY c.created_at DESC LIMIT 5"""),
                conn, params={"eid": entity_id}
            )
        st.markdown(f"#### Risk Assessments")
        st.dataframe(risk_df, use_container_width=True)
        st.markdown(f"#### Alerts")
        st.dataframe(alert_df, use_container_width=True)
        st.markdown(f"#### Compliance Checks")
        st.dataframe(comp_df, use_container_width=True)
        st.markdown(f"#### Linked Cases")
        st.dataframe(case_df, use_container_width=True)

# --- RISK ASSESSMENTS TAB ---
with tabs[1]:
    st.header("Risk Assessments")
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM public.risk_assessments ORDER BY assessment_date DESC LIMIT 50", conn)
    st.dataframe(df, use_container_width=True)

# --- ALERTS TAB ---
with tabs[2]:
    st.header("Alerts")
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM public.alerts ORDER BY created_at DESC LIMIT 50", conn)
    st.dataframe(df, use_container_width=True)

# --- COMPLIANCE CHECKS TAB ---
with tabs[3]:
    st.header("Compliance Checks")
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM public.compliance_checks ORDER BY checked_at DESC LIMIT 50", conn)
    st.dataframe(df, use_container_width=True)

# --- CASES TAB ---
with tabs[4]:
    st.header("Cases")
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM public.cases ORDER BY created_at DESC LIMIT 50", conn)
    st.dataframe(df, use_container_width=True)

# --- OSINT DATA TAB ---
with tabs[5]:
    st.header("OSINT Data")
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM public.osint_data ORDER BY collected_at DESC LIMIT 50", conn)
    st.dataframe(df, use_container_width=True)
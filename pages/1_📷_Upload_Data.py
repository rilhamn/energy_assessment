import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(layout="wide")

# ---------------------------------------
# Supabase
# ---------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------
# Sidebar – unit selector
# ---------------------------------------
st.sidebar.header("Settings")

unit = st.sidebar.selectbox(
    "Select Unit",
    ["Unit 1", "Unit 2"]
)

table_name = unit

# ---------------------------------------
# Page
# ---------------------------------------
st.title(f"{unit} – Upload Data and Processing")

# ======================================================
# Upload
# ======================================================
st.subheader("Upload raw data (CSV)")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.dataframe(df.head())

    required_cols = [
        "ts",
        "hp_mass_flow",
        "lp_mass_flow",
        "grs_mass_flow",
        "hp_pressure",
        "lp_pressure"
    ]

    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    if st.button("Upload to database"):

        rows = []

        for _, r in df.iterrows():
            rows.append({
                "ts": pd.to_datetime(r["ts"]).to_pydatetime(),
                "hp_mass_flow": float(r["hp_mass_flow"]),
                "lp_mass_flow": float(r["lp_mass_flow"]),
                "grs_mass_flow": float(r["grs_mass_flow"]),
                "hp_pressure": float(r["hp_pressure"]),
                "lp_pressure": float(r["lp_pressure"]),
                "hp_enthalpy": None,
                "lp_enthalpy": None,
                "inlet_energy": None
            })

        supabase.table(table_name) \
            .upsert(rows, on_conflict="ts") \
            .execute()

        st.success(f"Uploaded {len(rows)} rows to {table_name}")

# ======================================================
# Processing
# ======================================================
st.divider()
st.subheader("Process data")

if st.button("Process unprocessed rows"):

    resp = (
        supabase
        .table(table_name)
        .select(
            "id, hp_mass_flow, lp_mass_flow, hp_pressure, lp_pressure"
        )
        .is_("inlet_energy", "null")
        .execute()
    )

    data = resp.data

    if not data:
        st.info("No rows to process.")
        st.stop()

    count = 0

    for r in data:

        hp_m = r["hp_mass_flow"]
        lp_m = r["lp_mass_flow"]
        hp_p = r["hp_pressure"]
        lp_p = r["lp_pressure"]

        # dummy formula (replace later)
        hp_h = 1000 + 10 * hp_p
        lp_h = 900 + 8 * lp_p

        inlet_energy = hp_m * hp_h + lp_m * lp_h

        supabase.table(table_name) \
            .update({
                "hp_enthalpy": hp_h,
                "lp_enthalpy": lp_h,
                "inlet_energy": inlet_energy
            }) \
            .eq("id", r["id"]) \
            .execute()

        count += 1

    st.success(f"Processed {count} rows")

"""Streamlit dashboard that reads from the API service."""

import os

import httpx
import pandas as pd
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8081")
API_KEY = os.environ.get("API_KEY", "change-me")

st.set_page_config(page_title="Example dashboard", layout="wide")
st.title("Example dashboard")

rows = st.slider("Rows", min_value=5, max_value=500, value=50)

try:
    response = httpx.get(
        f"{API_URL}/data",
        params={"rows": rows},
        headers={"X-API-Key": API_KEY},
        timeout=5,
    )
    response.raise_for_status()
except httpx.HTTPError as exc:
    st.error(f"Could not reach the API at {API_URL}: {exc}")
else:
    df = pd.DataFrame(response.json())
    st.line_chart(df, x="x", y="y")
    st.dataframe(df, use_container_width=True)

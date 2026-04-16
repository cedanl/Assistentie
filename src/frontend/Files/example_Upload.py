import io

import pandas as pd
import streamlit as st

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
title = "File Upload"
icon = ":material/file_upload:"


# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
def save_uploaded_file(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile | None) -> None:
    """Reads the uploaded file once and stores raw bytes in session state.

    NOTE: You can move this file handler function to a separate file
    (frontend/utils or backend/utils - depending if it helps the UI or
    does a backend transformation needed for the project) and import it here
    """
    if uploaded_file is None:
        return
    st.session_state["file_bytes"] = uploaded_file.read()
    st.session_state["file_name"] = uploaded_file.name
    st.session_state["file_size"] = uploaded_file.size
    st.session_state["file_type"] = uploaded_file.type


@st.cache_data
def parse_csv(raw: bytes) -> pd.DataFrame:
    """Parse raw CSV bytes into a DataFrame, cached across reruns."""
    return pd.read_csv(io.BytesIO(raw))


# File upload section
st.header("📁 Upload File")
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file:
    save_uploaded_file(uploaded_file)
    st.success(f"File '{uploaded_file.name}' saved to session!")

# File inspection section
st.header("📋 File Inspector")
if "file_bytes" in st.session_state:
    st.write(f"**File Name:** {st.session_state['file_name']}")
    st.write(f"**File Size:** {st.session_state['file_size']} bytes")

    raw = st.session_state["file_bytes"]
    if st.session_state["file_type"] == "text/plain":
        content = raw.decode("utf-8")
        st.text_area("Preview:", content, height=200)
    else:
        st.dataframe(parse_csv(raw))
else:
    st.info("No file uploaded yet")

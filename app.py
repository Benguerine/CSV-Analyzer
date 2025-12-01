import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO


st.set_page_config(page_title="CSV Cleaner Pro", page_icon="🧹", layout="wide")
st.title("🧹 CSV Analyzer & Cleaner — Pro Version")


@st.cache_data
def load_csv(file):
    return pd.read_csv(file)


def fill_numeric(df, strategy):
    for col in df.select_dtypes(include=["float", "int"]).columns:
        if df[col].isnull().sum() > 0:
            if strategy == "Mean":
                df[col] = df[col].fillna(df[col].mean())
            elif strategy == "Median":
                df[col] = df[col].fillna(df[col].median())
            elif strategy == "Zero":
                df[col] = df[col].fillna(0)
    return df


def fill_categorical(df, strategy):
    for col in df.select_dtypes(include=["object"]).columns:
        if df[col].isnull().sum() > 0:
            if strategy == "Mode":
                df[col] = df[col].fillna(df[col].mode()[0])
            elif strategy == "Forward Fill":
                df[col] = df[col].fillna(method="ffill")
            elif strategy == "Backward Fill":
                df[col] = df[col].fillna(method="bfill")
    return df


def create_missing_report(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    report = pd.DataFrame({"Column": missing.index, "Missing Count": missing.values})
    return report


def convert_df_to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer



st.sidebar.header("⚙️ Cleaning Options")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = load_csv(uploaded_file)

    st.subheader("📄 Original Dataset Preview")
    st.dataframe(df.head())

    # Missing Report
    report = create_missing_report(df)

    st.subheader("🔍 Missing Values Analysis")

    if report.empty:
        st.success("✨ No missing values found. Dataset is clean!")
    else:
        st.warning("⚠️ Missing values detected in the dataset.")
        st.dataframe(report)

        # Heatmap
        st.subheader("🔥 Missing Values Heatmap")

        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
        st.pyplot(fig)

        # Cleaning Options
        st.subheader("🧪 Cleaning Strategy")

        numeric_strategy = st.sidebar.selectbox(
            "Numeric Strategy", ["Mean", "Median", "Zero"]
        )

        cat_strategy = st.sidebar.selectbox(
            "Categorical Strategy", ["Mode", "Forward Fill", "Backward Fill"]
        )

        drop_rows = st.sidebar.checkbox("Drop Rows with ANY Missing Value")
        drop_cols = st.sidebar.checkbox("Drop Columns with ANY Missing Value")

        df_cleaned = df.copy()

        # Apply Drops
        if drop_rows:
            df_cleaned = df_cleaned.dropna()

        if drop_cols:
            df_cleaned = df_cleaned.dropna(axis=1)

        # Apply Filling Only If Not Dropped
        if not drop_rows and not drop_cols:
            df_cleaned = fill_numeric(df_cleaned, numeric_strategy)
            df_cleaned = fill_categorical(df_cleaned, cat_strategy)

        st.success("🎉 Cleaning process completed!")

        st.subheader("📂 Cleaned Dataset Preview")
        st.dataframe(df_cleaned.head())

        # Downloads
        cleaned_csv = convert_df_to_csv(df_cleaned)
        report_csv = convert_df_to_csv(report)

        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=cleaned_csv,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
        )

        if not report.empty:
            st.download_button(
                label="⬇️ Download Missing Value Report",
                data=report_csv,
                file_name="missing_value_report.csv",
                mime="text/csv",
            )

else:
    st.info("📤 Please upload a CSV file to begin.")

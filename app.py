import streamlit as st
import pandas as pd

from core_mfn import calculate_mfn_detractors_weekly
from core_fba import calculate_fba_detractors_weekly


# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="MFN & FBA Weekly Detractor Analyzer",
    layout="wide"
)

st.title("📊 MFN & FBA Weekly Detractor Web App")

st.markdown("""
Bu uygulama:
- QuickSight export edilen CSV dosyalarıyla çalışır  
- Haftanın **Pazar günü başladığı** varsayımıyla analiz yapar  
- MFN ve FBA için **haftalık detractor** hesaplar  
- Account Manager bazlı filtreleme sunar
""")


# -------------------------------------------------
# Sidebar – Account Manager Mapping
# -------------------------------------------------
st.sidebar.header("👤 Account Manager Mapping")

am_file = st.sidebar.file_uploader(
    "OHL_Accounts Excel yükleyin",
    type=["xlsx"]
)

df_am = None
if am_file:
    try:
        df_am = pd.read_excel(
            am_file,
            sheet_name="OHL_Accounts",
            header=1
        )
        df_am = df_am[[
            "Merchant Customer ID",
            "New Account Manager"
        ]].dropna(subset=["Merchant Customer ID"])
        st.sidebar.success("AM mapping yüklendi")
    except Exception as e:
        st.sidebar.error("AM mapping okunamadı")
        st.sidebar.exception(e)


# -------------------------------------------------
# Tabs
# -------------------------------------------------
tab_mfn, tab_fba = st.tabs(["🟦 MFN", "🟧 FBA"])


# =================================================
# MFN TAB
# =================================================
with tab_mfn:
    st.subheader("🟦 MFN Weekly Detractor")

    mfn_file = st.file_uploader(
        "MFN CSV dosyasını yükleyin",
        type=["csv"],
        key="mfn"
    )

    if mfn_file:
        try:
            df_mfn = pd.read_csv(mfn_file)
            df_mfn["snapshot_day"] = pd.to_datetime(df_mfn["snapshot_day"])

            st.success("MFN dosyası yüklendi")

            result_mfn = calculate_mfn_detractors_weekly(df_mfn)

            if result_mfn.empty:
                st.warning("MFN için sonuç üretilemedi.")
            else:
                # 🔗 AM merge
                if df_am is not None:
                    result_mfn = result_mfn.merge(
                        df_am,
                        left_on="merchant_customer_id",
                        right_on="Merchant Customer ID",
                        how="left"
                    )
                    result_mfn["New Account Manager"] = (
                        result_mfn["New Account Manager"]
                        .fillna("NA")
                    )

                result_mfn = result_mfn.sort_values("detractor_score")

                # 🎯 AM Filter
                if "New Account Manager" in result_mfn.columns:
                    am_list = sorted(result_mfn["New Account Manager"].unique())
                    selected_am = st.selectbox(
                        "👤 Account Manager filtrele",
                        ["ALL"] + am_list
                    )

                    if selected_am != "ALL":
                        view_mfn = result_mfn[
                            result_mfn["New Account Manager"] == selected_am
                        ]
                    else:
                        view_mfn = result_mfn
                else:
                    view_mfn = result_mfn

                st.metric(
                    "📊 Total MFN Impact",
                    float(view_mfn["detractor_score"].sum())
                )

                st.dataframe(view_mfn, use_container_width=True)

                st.download_button(
                    "⬇️ Download MFN Result",
                    data=view_mfn.to_csv(index=False).encode("utf-8"),
                    file_name="mfn_weekly_detractors.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error("MFN analizinde hata oluştu")
            st.exception(e)


# =================================================
# FBA TAB
# =================================================
with tab_fba:
    st.subheader("🟧 FBA Weekly Detractor")

    sellerflex_file = st.file_uploader(
        "SellerFlex CSV yükleyin",
        type=["csv"],
        key="sellerflex"
    )

    fba_file = st.file_uploader(
        "FBA CSV yükleyin",
        type=["csv"],
        key="fba"
    )

    if sellerflex_file and fba_file:
        try:
            df_sellerflex = pd.read_csv(sellerflex_file)
            df_fba = pd.read_csv(fba_file)

            df_sellerflex["snapshot_day"] = pd.to_datetime(df_sellerflex["snapshot_day"])
            df_fba["snapshot_day"] = pd.to_datetime(df_fba["snapshot_day"])

            result_fba = calculate_fba_detractors_weekly(
                fba_df=df_fba,
                sellerflex_df=df_sellerflex
            )

            if result_fba.empty:
                st.warning("FBA için sonuç üretilemedi.")
            else:
                # 🔗 AM merge
                if df_am is not None:
                    result_fba = result_fba.merge(
                        df_am,
                        left_on="merchant_customer_id",
                        right_on="Merchant Customer ID",
                        how="left"
                    )
                    result_fba["New Account Manager"] = (
                        result_fba["New Account Manager"]
                        .fillna("NA")
                    )

                result_fba = result_fba.sort_values("detractor_score")

                # 🎯 AM Filter
                if "New Account Manager" in result_fba.columns:
                    am_list = sorted(result_fba["New Account Manager"].unique())
                    selected_am = st.selectbox(
                        "👤 Account Manager filtrele",
                        ["ALL"] + am_list,
                        key="fba_am"
                    )

                    if selected_am != "ALL":
                        view_fba = result_fba[
                            result_fba["New Account Manager"] == selected_am
                        ]
                    else:
                        view_fba = result_fba
                else:
                    view_fba = result_fba

                st.metric(
                    "📊 Total FBA Impact",
                    float(view_fba["detractor_score"].sum())
                )

                st.dataframe(view_fba, use_container_width=True)

                st.download_button(
                    "⬇️ Download FBA Result",
                    data=view_fba.to_csv(index=False).encode("utf-8"),
                    file_name="fba_weekly_detractors.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error("FBA analizinde hata oluştu")
            st.exception(e)

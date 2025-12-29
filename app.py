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

**Genel Mantık:**
- Üst dönem: Bu haftada bugüne kadar geçen gün sayısı
- Alt dönem: Onun hemen öncesindeki maksimum 7 gün
""")


# -------------------------------------------------
# Tabs
# -------------------------------------------------
tab_mfn, tab_fba = st.tabs(["🟦 MFN", "🟧 FBA"])


# =================================================
# MFN TAB
# =================================================
with tab_mfn:
    st.subheader("🟦 MFN Weekly Top Detractor")

    mfn_file = st.file_uploader(
        "MFN CSV dosyasını yükleyin",
        type=["csv"],
        key="mfn"
    )

    if mfn_file:
        try:
            df_mfn = pd.read_csv(mfn_file)
            df_mfn["snapshot_day"] = pd.to_datetime(df_mfn["snapshot_day"])

            st.success("MFN dosyası yüklendi.")

            with st.expander("📅 Dataset Bilgisi"):
                st.write("En erken tarih:", df_mfn["snapshot_day"].min().date())
                st.write("En güncel tarih:", df_mfn["snapshot_day"].max().date())
                st.write("Merchant sayısı:", df_mfn["merchant_customer_id"].nunique())

            result_mfn = calculate_mfn_detractors_weekly(df_mfn)

            if result_mfn.empty:
                st.warning("MFN için sonuç üretilemedi.")
            else:
                result_mfn = result_mfn.sort_values("detractor_score")

                total_mfn = result_mfn["detractor_score"].sum()
                st.metric("📊 Total MFN Impact", float(total_mfn))

                st.subheader("🔥 Top 3 MFN Detractors")
                st.dataframe(result_mfn.head(3), use_container_width=True)

                st.subheader("📋 All MFN Detractors")
                st.dataframe(result_mfn, use_container_width=True)

                st.download_button(
                    "⬇️ Download MFN Result CSV",
                    data=result_mfn.to_csv(index=False).encode("utf-8"),
                    file_name="mfn_weekly_detractors.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error("MFN analizinde hata oluştu:")
            st.exception(e)


# =================================================
# FBA TAB
# =================================================
with tab_fba:
    st.subheader("🟧 FBA Weekly Top Detractor")

    sellerflex_file = st.file_uploader(
        "SellerFlex CSV dosyasını yükleyin",
        type=["csv"],
        key="sellerflex"
    )

    fba_file = st.file_uploader(
        "FBA CSV dosyasını yükleyin",
        type=["csv"],
        key="fba"
    )

    if sellerflex_file and fba_file:
        try:
            df_sellerflex = pd.read_csv(sellerflex_file)
            df_fba = pd.read_csv(fba_file)

            df_sellerflex["snapshot_day"] = pd.to_datetime(df_sellerflex["snapshot_day"])
            df_fba["snapshot_day"] = pd.to_datetime(df_fba["snapshot_day"])

            st.success("SellerFlex ve FBA dosyaları yüklendi.")

            result_fba = calculate_fba_detractors_weekly(
                fba_df=df_fba,
                sellerflex_df=df_sellerflex
            )

            if result_fba.empty:
                st.warning("FBA için sonuç üretilemedi.")
            else:
                result_fba = result_fba.sort_values("detractor_score")

                total_fba = result_fba["detractor_score"].sum()
                st.metric("📊 Total FBA Impact", float(total_fba))

                st.subheader("🔥 Top 10 FBA Detractors")
                st.dataframe(result_fba.head(10), use_container_width=True)

                st.subheader("📋 All FBA Detractors")
                st.dataframe(result_fba, use_container_width=True)

                st.download_button(
                    "⬇️ Download FBA Result CSV",
                    data=result_fba.to_csv(index=False).encode("utf-8"),
                    file_name="fba_weekly_detractors.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error("FBA analizinde hata oluştu:")
            st.exception(e)

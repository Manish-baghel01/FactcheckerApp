import streamlit as st
import PyPDF2
import re
from duckduckgo_search import DDGS
import pandas as pd

st.title("Fact Checker App")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:

    try:
        reader = PyPDF2.PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        st.subheader("Extracted Text")
        st.write(text[:2000])

        claims = re.findall(r'[^.]*\d+[^.]*\.', text)

        if not claims:
            st.warning("No claims found.")
            st.stop()

        st.subheader("Claims Found")

        for claim in claims:
            st.write(claim)

        report = []

        with DDGS() as ddgs:

            for claim in claims:

                try:

                    results = list(ddgs.text(claim, max_results=1))

                    if len(results) > 0:

                        source = results[0].get(
                            "href",
                            results[0].get(
                                "url",
                                "No URL Available"
                            )
                        )

                        st.success("✅ VERIFIED")
                        st.write(claim)
                        st.write(source)

                        report.append({
                            "Claim": claim,
                            "Status": "Verified",
                            "Source": source
                        })

                    else:

                        st.error("❌ FALSE")

                        report.append({
                            "Claim": claim,
                            "Status": "False",
                            "Source": "-"
                        })

                except Exception as e:

                    report.append({
                        "Claim": claim,
                        "Status": "Error",
                        "Source": str(e)
                    })

        df = pd.DataFrame(report)

        st.subheader("Final Report")
        st.dataframe(df)

        csv = df.to_csv(index=False)

        st.download_button(
            "Download Report",
            csv,
            "factcheck_report.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(f"Error: {e}")
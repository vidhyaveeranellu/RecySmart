

import streamlit as st
import requests

st.set_page_config(page_title="RecySmart", layout="centered")
st.title("♻️ RecySmart – Smart Waste Management")

city = st.text_input("Enter City (example: Chennai)")
image = st.file_uploader("Upload Waste Image", type=["jpg","png","jpeg"])

if st.button("Predict"):
    if city and image:
        with st.spinner("Analyzing..."):
            response = requests.post(
                "http://127.0.0.1:5000/predict",
                files={"image": image},
                data={"city": city}
            )

        # Safe JSON handling
        try:
            result = response.json()
        except:
            st.error("Flask did not return JSON.")
            st.text("Raw response:")
            st.text(response.text)
            st.stop()

        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Prediction Successful")

            st.subheader("Waste Analysis")
            st.info(f"Waste Type: {result['waste_type']}")

            st.subheader("Recommended Product")
            st.write("Product:", result["product"])
            st.write("Lifetime:", result["lifetime"])
            st.write("Best Area:", result["best_area"])

            st.subheader("Climate Data Used")
            st.write("Temperature Avg:", result["temperature_avg"], "°C")
            st.write("Rainfall:", result["rainfall"], "mm")
            st.write("Humidity:", result["humidity"], "%")
            st.write("AQI:", result["aqi"])
            st.write("Cloud Cover:", result["cloud_cover"], "%")

            st.subheader("Reason")
            st.write(result["reason"])
    else:
        st.warning("Please enter city and upload an image")

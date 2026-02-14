import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import pandas as pd
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load model
model = tf.keras.models.load_model("model.h5")
classes = ["Industrial", "Medical", "Organic", "Plastic", "Other"]

# Load datasets
product_db = pd.read_csv("product_db.csv")
climate_db = pd.read_csv("climate_db.csv")

# 🔥 CLEAN ALL COLUMN NAMES (this fixes EVERYTHING)
climate_db.columns = (
    climate_db.columns
    .str.strip()
    .str.replace("  ", " ")
)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["image"]
        city = request.form["city"]

        # Image preprocessing
        img = Image.open(file).convert("RGB").resize((224,224))
        img_arr = np.array(img) / 255.0
        img_arr = img_arr.reshape(1,224,224,3)

        # Prediction
        pred = model.predict(img_arr)
        waste_type = classes[np.argmax(pred)]

        # Climate data
        city_row = climate_db[climate_db["City"] == city]
        if city_row.empty:
            return jsonify({"error": "City not found"})

        city_data = city_row.iloc[0]

        # Now these work perfectly
        temp = float(city_data["Temperature_Avg"])
        rain = float(city_data["Rainfall (mm)"])
        humidity = float(city_data["Humidity (%)"])
        aqi = int(city_data["AQI"])
        cloud = float(city_data["Cloud_Cover (%)"])

        # Product recommendation
        rec_row = product_db[
            (product_db["waste_type"] == waste_type) &
            (product_db["min_temp"] <= temp) &
            (product_db["max_temp"] >= temp)
        ]

        if rec_row.empty:
            return jsonify({"error": "No suitable product found"})

        rec = rec_row.iloc[0]

        return jsonify({
            "waste_type": waste_type,
            "product": rec["product"],
            "lifetime": rec["lifetime"],
            "best_area": rec["best_area"],
            "temperature_avg": temp,
            "rainfall": rain,
            "humidity": humidity,
            "aqi": aqi,
            "cloud_cover": cloud,
            "reason": "Recommended using climate and waste analysis"
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(port=5000)

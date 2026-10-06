from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import joblib
import os


# --------------------------------------------------
# 1. CREATE FLASK APPLICATION
# --------------------------------------------------

app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# 2. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "credit_model.pkl"
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "credit_data.xlsx"
)

FRONTEND_PATH = os.path.join(
    BASE_DIR,
    "frontend"
)


# --------------------------------------------------
# 3. LOAD TRAINED MODEL
# --------------------------------------------------

model = joblib.load(MODEL_PATH)

print("Credit scoring model loaded successfully.")


# --------------------------------------------------
# 4. FEATURE ENGINEERING
# --------------------------------------------------

def add_features(data):

    data["Credit_Age_Ratio"] = (
        data["Camt"] / data["age"]
    )

    data["Duration_Age_Ratio"] = (
        data["Cdur"] / data["age"]
    )

    data["Credit_Per_Month"] = (
        data["Camt"] / data["Cdur"]
    )

    return data


# --------------------------------------------------
# 5. HOME ROUTE
# --------------------------------------------------

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_PATH,
        "index.html"
    )


# --------------------------------------------------
# 6. HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "model": "Random Forest Credit Scoring Model"
    })


# --------------------------------------------------
# 7. PREDICTION ROUTE
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        if data is None:

            return jsonify({
                "error": "No JSON data received"
            }), 400


        # Convert input into DataFrame
        input_data = pd.DataFrame([data])


        # Add engineered features
        input_data = add_features(
            input_data
        )


        # Make prediction
        prediction = model.predict(
            input_data
        )[0]


        # Get probabilities
        probability = model.predict_proba(
            input_data
        )[0]


        # Convert prediction
        if prediction == 1:

            credit_status = "Good"

        else:

            credit_status = "Bad"


        # Probability of Good credit
        good_probability = probability[1] * 100

        # Probability of Bad credit
        bad_probability = probability[0] * 100


        return jsonify({

            "prediction": credit_status,

            "prediction_code": int(
                prediction
            ),

            "good_probability": round(
                good_probability,
                2
            ),

            "bad_probability": round(
                bad_probability,
                2
            )
        })


    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500


# --------------------------------------------------
# 8. GET DATASET OPTIONS
# --------------------------------------------------

@app.route("/options", methods=["GET"])
def get_options():

    try:

        df = pd.read_excel(
            DATASET_PATH
        )


        categorical_columns = [

            "Cbal",
            "Chist",
            "Cpur",
            "Sbal",
            "Edur",
            "MSG",
            "Oparties",
            "Rdur",
            "Prop",
            "inPlans",
            "Htype",
            "JobType",
            "telephone",
            "foreign"

        ]


        options = {}


        for column in categorical_columns:

            values = (
                df[column]
                .dropna()
                .unique()
                .tolist()
            )

            options[column] = values


        return jsonify(options)


    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500


# --------------------------------------------------
# 9. SERVE FRONTEND FILES
# --------------------------------------------------

@app.route("/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        FRONTEND_PATH,
        filename
    )


# --------------------------------------------------
# 10. LOCAL DEVELOPMENT
# --------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)

    print(
        "Credit Scoring Web API"
    )

    print("=" * 60)

    print(
        "Server running at:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print("=" * 60)


    app.run(
        debug=True,
        port=5000
    )
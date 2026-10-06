import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve
)

import matplotlib.pyplot as plt
import seaborn as sns
import joblib


# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

file_path = "../dataset/credit_data.xlsx"

df = pd.read_excel(file_path)

print("Dataset loaded successfully.")
print("Dataset shape:", df.shape)


# --------------------------------------------------
# 2. SEPARATE FEATURES AND TARGET
# --------------------------------------------------

X = df.drop("creditScore", axis=1)

y = df["creditScore"].map({
    "good": 1,
    "bad": 0
})

print("\nTarget distribution:")
print(y.value_counts())


# --------------------------------------------------
# 3. FEATURE ENGINEERING
# --------------------------------------------------

# Credit amount to age ratio
X["Credit_Age_Ratio"] = X["Camt"] / X["age"]

# Credit duration to age ratio
X["Duration_Age_Ratio"] = X["Cdur"] / X["age"]

# Credit amount per credit duration
X["Credit_Per_Month"] = X["Camt"] / X["Cdur"]


# --------------------------------------------------
# 4. IDENTIFY NUMERICAL AND CATEGORICAL FEATURES
# --------------------------------------------------

numerical_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

categorical_features = X.select_dtypes(
    include=["object", "str"]
).columns.tolist()


print("\nNumerical Features:")
print(numerical_features)

print("\nCategorical Features:")
print(categorical_features)


# --------------------------------------------------
# 5. PREPROCESSING
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            StandardScaler(),
            numerical_features
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        )
    ]
)


# --------------------------------------------------
# 6. TRAIN-TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# --------------------------------------------------
# 7. CREATE MODELS
# --------------------------------------------------

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=6,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )
}


# --------------------------------------------------
# 8. TRAIN AND EVALUATE MODELS
# --------------------------------------------------

results = []

trained_models = {}


for model_name, model in models.items():

    print("\n" + "=" * 60)
    print(model_name)
    print("=" * 60)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    # Train
    pipeline.fit(X_train, y_train)

    # Predict
    y_pred = pipeline.predict(X_test)

    # Prediction probabilities
    y_probability = pipeline.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        y_probability
    )

    print("Accuracy :", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall   :", round(recall, 4))
    print("F1-Score :", round(f1, 4))
    print("ROC-AUC  :", round(roc_auc, 4))

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["Bad", "Good"]
        )
    )

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Store results
    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1,
        "ROC-AUC": roc_auc
    })

    trained_models[model_name] = pipeline


# --------------------------------------------------
# 9. MODEL COMPARISON
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n")
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# --------------------------------------------------
# 10. SAVE MODEL COMPARISON
# --------------------------------------------------

results_df.to_csv(
    "../models/model_comparison.csv",
    index=False
)


# --------------------------------------------------
# 11. SELECT MODEL
# --------------------------------------------------

# We use ROC-AUC as the selection metric because
# credit-risk classification involves probability
# ranking and class imbalance.

best_model_name = results_df.loc[
    results_df["ROC-AUC"].idxmax(),
    "Model"
]

best_model = trained_models[best_model_name]

print("\nSelected model:", best_model_name)


# --------------------------------------------------
# 12. SAVE BEST MODEL
# --------------------------------------------------

joblib.dump(
    best_model,
    "../models/credit_model.pkl"
)

print("\nModel saved successfully.")

print(
    "Saved file: ../models/credit_model.pkl"
)


# --------------------------------------------------
# 13. CONFUSION MATRIX FOR BEST MODEL
# --------------------------------------------------

best_predictions = best_model.predict(X_test)

cm = confusion_matrix(
    y_test,
    best_predictions
)

plt.figure(figsize=(6, 5))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Bad", "Good"],
    yticklabels=["Bad", "Good"]
)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - " + best_model_name)

plt.tight_layout()

plt.savefig(
    "../images/confusion_matrix.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 14. ROC CURVE
# --------------------------------------------------

best_probability = best_model.predict_proba(
    X_test
)[:, 1]

fpr, tpr, thresholds = roc_curve(
    y_test,
    best_probability
)

best_auc = roc_auc_score(
    y_test,
    best_probability
)

plt.figure(figsize=(7, 5))

plt.plot(
    fpr,
    tpr,
    label="ROC-AUC = " + str(round(best_auc, 3))
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title(
    "ROC Curve - " + best_model_name
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "../images/roc_curve.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 15. FINISHED
# --------------------------------------------------

print("\nTraining completed successfully.")

print("\nGenerated files:")

print("1. models/model_comparison.csv")
print("2. models/credit_model.pkl")
print("3. images/confusion_matrix.png")
print("4. images/roc_curve.png")
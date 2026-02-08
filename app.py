from flask import Flask, render_template, request
import joblib
import json
import pandas as pd
import sys
import warnings

app = Flask(__name__)

MODEL_FILE = "churn_model_pipeline.joblib"
META_FILE = "churn_model_metadata.json"

# Suppress sklearn version warnings (optional)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Load model + metadata on startup dengan error handling
model = None
meta = {}
THRESHOLD = 0.5
FEATURE_COLS = []

try:
    print("Memuat model...")
    model = joblib.load(MODEL_FILE)
    print("✓ Model berhasil dimuat")
    
    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)
    
    THRESHOLD = float(meta.get("threshold", 0.5))
    FEATURE_COLS = meta["feature_columns"]
    print(f"✓ Metadata berhasil dimuat (threshold: {THRESHOLD})")
    
except AttributeError as e:
    print("\n" + "="*60)
    print("ERROR: Masalah kompatibilitas versi scikit-learn!")
    print("="*60)
    print(f"Detail error: {e}")
    print("\nSolusi:")
    print("1. Install versi scikit-learn yang sama dengan saat model dibuat (1.6.1):")
    print("   pip install scikit-learn==1.6.1")
    print("\n2. Atau install semua dependencies dari requirements.txt:")
    print("   pip install -r requirements.txt")
    print("\n3. Setelah itu, jalankan ulang aplikasi.")
    print("="*60 + "\n")
    sys.exit(1)
    
except FileNotFoundError as e:
    print(f"\nERROR: File tidak ditemukan - {e}")
    print("Pastikan file berikut ada di direktori yang sama:")
    print(f"  - {MODEL_FILE}")
    print(f"  - {META_FILE}\n")
    sys.exit(1)
    
except Exception as e:
    print(f"\nERROR: Gagal memuat model - {e}")
    print("Periksa file model dan metadata.\n")
    sys.exit(1)

# Helper: cast input safely
def to_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default

def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

@app.get("/")
def index():
    # Kirim threshold ke UI (biar user tahu batasnya)
    return render_template("index.html", threshold=THRESHOLD)

@app.post("/predict")
def predict():
    if model is None:
        return render_template("result.html",
            threshold=THRESHOLD,
            prediction=0,
            label="ERROR",
            proba=0.0,
            proba_pct=0.0,
            risk_level="Error",
            form_data={},
            error="Model tidak tersedia. Periksa kompatibilitas versi scikit-learn."
        )
    
    # Ambil input dari form (nama harus sama dengan field di index.html)
    payload = {
        "CreditScore": to_int(request.form.get("CreditScore")),
        "Geography": request.form.get("Geography", "France"),
        "Gender": request.form.get("Gender", "Male"),
        "Age": to_int(request.form.get("Age")),
        "Tenure": to_int(request.form.get("Tenure")),
        "Balance": to_float(request.form.get("Balance")),
        "NumOfProducts": to_int(request.form.get("NumOfProducts")),
        "HasCrCard": to_int(request.form.get("HasCrCard")),
        "IsActiveMember": to_int(request.form.get("IsActiveMember")),
        "EstimatedSalary": to_float(request.form.get("EstimatedSalary")),
    }

    try:
        # Pastikan kolom lengkap dan urutan benar
        X_in = pd.DataFrame([payload])

        # Kalau metadata punya kolom lain (jarang), kita isi default aman
        for c in FEATURE_COLS:
            if c not in X_in.columns:
                X_in[c] = 0

        X_in = X_in[FEATURE_COLS]

        # Prediksi probabilitas churn
        proba_churn = float(model.predict_proba(X_in)[:, 1][0])
        pred = int(proba_churn >= THRESHOLD)
        
        # Untuk UI
        proba_pct = round(proba_churn * 100, 2)
        label = "CHURN" if pred == 1 else "TIDAK CHURN"
        risk_level = (
            "Rendah" if proba_churn < 0.33 else
            "Sedang" if proba_churn < 0.66 else
            "Tinggi"
        )

        return render_template(
            "result.html",
            threshold=THRESHOLD,
            prediction=pred,
            label=label,
            proba=proba_churn,
            proba_pct=proba_pct,
            risk_level=risk_level,
            form_data=payload,
            error=None
        )
    except Exception as e:
        return render_template("result.html",
            threshold=THRESHOLD,
            prediction=0,
            label="ERROR",
            proba=0.0,
            proba_pct=0.0,
            risk_level="Error",
            form_data=payload,
            error=f"Error saat prediksi: {str(e)}"
        )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from analyzer.landmark import FaceLandmarkDetector
from analyzer.harmony import HarmonyAnalyzer
from analyzer.angularity import AngularityAnalyzer
from analyzer.dimorphism import DimorphismAnalyzer
from analyzer.health import HealthAnalyzer
from analyzer.scoring import ScoringEngine

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize analyzers
detector = FaceLandmarkDetector()
harmony = HarmonyAnalyzer(detector)
angularity = AngularityAnalyzer(detector)
dimorphism = DimorphismAnalyzer(detector)
health = HealthAnalyzer(detector)
scoring = ScoringEngine()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "photo" not in request.files:
        return jsonify({"error": "No photo uploaded"}), 400

    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save uploaded file
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        # Detect landmarks
        result = detector.detect(filepath)
        if result is None:
            return jsonify({"error": "No face detected. Please upload a clear, front-facing photo."}), 400

        # Run all analyzers
        harmony_result = harmony.analyze(result)
        angularity_result = angularity.analyze(result)
        dimorphism_result = dimorphism.analyze(result)
        health_result = health.analyze(result, filepath)

        # Compute scores
        scores = scoring.compute_scores(
            harmony_result, angularity_result, dimorphism_result, health_result
        )

        return jsonify({
            "success": True,
            "scores": scores,
            "details": {
                "harmony": harmony_result,
                "angularity": angularity_result,
                "dimorphism": dimorphism_result,
                "health": health_result,
            },
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

import numpy as np
from typing import Optional


class DimorphismAnalyzer:
    """Analyzes gender-specific facial trait characteristics."""

    def __init__(self, detector):
        self.detector = detector

    def analyze(self, landmarks: dict) -> dict:
        """Run dimorphism analysis across key gender markers."""
        lm = landmarks["landmarks"]
        d = self.detector.distance
        angle = self.detector.angle_between

        results = {}

        # 1. Brow Ridge Prominence
        results["brow_ridge"] = self._brow_ridge(lm, d)

        # 2. Jaw Squareness
        results["jaw_squareness"] = self._jaw_squareness(lm, d, angle)

        # 3. Chin Squareness
        results["chin_squareness"] = self._chin_squareness(lm, d)

        # 4. Midface Fullness
        results["midface_fullness"] = self._midface_fullness(lm, d)

        # 5. Lip Fullness
        results["lip_fullness"] = self._lip_fullness(lm, d)

        # 6. Brow Position & Thickness
        results["brow_position"] = self._brow_position(lm, d)

        # 7. Eye Size Relative to Face
        results["eye_size"] = self._eye_size(lm, d)

        # 8. Composite Score
        scores = [v["score"] for v in results.values()]
        results["composite"] = {
            "score": round(np.mean(scores), 1),
            "masculine_traits": self._count_masculine(results),
            "feminine_traits": self._count_feminine(results),
            "description": "Overall balance of masculine and feminine facial traits",
        }

        return results

    def _brow_ridge(self, lm, d) -> dict:
        """Prominence of the brow ridge — more prominent = more masculine."""
        brow_left = lm["brow_left_outer"]
        brow_right = lm["brow_right_outer"]
        eye_top_left = lm["eye_left_top"]
        eye_top_right = lm["eye_right_top"]

        # Distance from brow to eye top (larger = more prominent brow ridge)
        left_brow_eye = d(brow_left, eye_top_left)
        right_brow_eye = d(brow_right, eye_top_right)
        avg_brow_eye = (left_brow_eye + right_brow_eye) / 2

        eye_width = (d(lm["eye_left_outer"], lm["eye_left_inner"]) +
                     d(lm["eye_right_outer"], lm["eye_right_inner"])) / 2

        ratio = avg_brow_eye / eye_width if eye_width > 0 else 0

        # Higher ratio = more prominent brow (masculine trait)
        # Moderate prominence scores highest for overall attractiveness
        score = 5.0 + (ratio - 0.3) * 15
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "trait": "masculine" if ratio > 0.35 else "feminine",
            "description": "Brow ridge prominence — more pronounced = more masculine",
        }

    def _jaw_squareness(self, lm, d, angle) -> dict:
        """How square the jaw appears — masculine trait."""
        jaw_left = lm["jaw_left_mid"]
        jaw_right = lm["jaw_right_mid"]
        chin_left = lm["chin_left"]
        chin_right = lm["chin_right"]

        jaw_width = d(jaw_left, jaw_right)
        chin_width = d(chin_left, chin_right)

        # Squareness ratio: jaw width to chin width (closer to 1.0 = squarer)
        if chin_width == 0:
            ratio = 1.0
        else:
            ratio = jaw_width / chin_width

        # Square jaw (ratio closer to 1.0) = more masculine
        score = 5.0 + (ratio - 1.0) * 10
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "trait": "masculine" if ratio > 1.2 else "feminine",
            "description": "Jaw squareness — wider, squarer jaw = more masculine",
        }

    def _chin_squareness(self, lm, d) -> dict:
        """How square the chin appears — masculine trait."""
        chin_left = lm["chin_left"]
        chin_right = lm["chin_right"]
        chin_tip = lm["chin_tip"]

        chin_width = d(chin_left, chin_right)
        chin_height = d(lm["lip_lower_bottom"], chin_tip)

        ratio = chin_width / chin_height if chin_height > 0 else 1.0

        # Wider, squarer chin = more masculine
        score = 5.0 + (ratio - 0.8) * 8
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "trait": "masculine" if ratio > 1.0 else "feminine",
            "description": "Chin squareness — wider chin = more masculine",
        }

    def _midface_fullness(self, lm, d) -> dict:
        """Fullness of the midface area — feminine trait."""
        cheek_left = lm["cheek_left"]
        cheek_right = lm["cheek_right"]
        nose_left = lm["nose_left"]
        nose_right = lm["nose_right"]

        face_width = d(lm["face_left"], lm["face_right"])

        # Midface prominence: cheek width relative to face
        cheek_width = d(cheek_left, cheek_right)
        cheek_ratio = cheek_width / face_width if face_width > 0 else 0

        # Fuller midface = more feminine
        score = 5.0 + (0.95 - cheek_ratio) * 30
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "ratio": round(cheek_ratio, 3),
            "trait": "feminine" if cheek_ratio > 0.90 else "masculine",
            "description": "Midface fullness — rounder, fuller midface = more feminine",
        }

    def _lip_fullness(self, lm, d) -> dict:
        """Lip volume and fullness — feminine trait."""
        upper_lip_top = lm["lip_upper_top"]
        upper_lip_mid = lm["lip_upper_mid"]
        lower_lip_bottom = lm["lip_lower_bottom"]
        lower_lip_mid = lm["lip_lower_mid"]

        upper_lip_height = d(upper_lip_top, upper_lip_mid)
        lower_lip_height = d(lower_lip_mid, lower_lip_bottom)
        total_lip = upper_lip_height + lower_lip_height

        mouth_width = d(lm["mouth_left"], lm["mouth_right"])
        lip_width_ratio = total_lip / mouth_width if mouth_width > 0 else 0

        # Fuller lips = more feminine
        score = 5.0 + (lip_width_ratio - 0.15) * 40
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "ratio": round(lip_width_ratio, 3),
            "upper_lower_ratio": round(upper_lip_height / lower_lip_height if lower_lip_height > 0 else 0, 2),
            "trait": "feminine" if lip_width_ratio > 0.18 else "masculine",
            "description": "Lip fullness — thicker lips = more feminine trait",
        }

    def _brow_position(self, lm, d) -> dict:
        """Brow height and arch — position relative to eyes."""
        brow_left = lm["brow_left_mid"]
        eye_top_left = lm["eye_left_top"]
        eye_bottom_left = lm["eye_left_bottom"]

        # Brow to eye distance
        brow_eye_dist = d(brow_left, eye_top_left)
        eye_height = d(eye_top_left, eye_bottom_left)

        ratio = brow_eye_dist / eye_height if eye_height > 0 else 1.0

        # Higher brows (larger ratio) = more feminine
        score = 5.0 + (ratio - 1.0) * 8
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "trait": "feminine" if ratio > 1.2 else "masculine",
            "description": "Brow position — higher, more arched brows = more feminine",
        }

    def _eye_size(self, lm, d) -> dict:
        """Eye size relative to face — larger eyes = more feminine."""
        left_eye_w = d(lm["eye_left_outer"], lm["eye_left_inner"])
        right_eye_w = d(lm["eye_right_outer"], lm["eye_right_inner"])
        avg_eye_w = (left_eye_w + right_eye_w) / 2

        face_w = d(lm["face_left"], lm["face_right"])

        ratio = avg_eye_w / face_w if face_w > 0 else 0

        # Larger eyes relative to face = more feminine
        score = 5.0 + (ratio - 0.10) * 40
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "trait": "feminine" if ratio > 0.12 else "masculine",
            "description": "Eye size relative to face — larger eyes = more feminine",
        }

    def _count_masculine(self, results) -> int:
        return sum(1 for v in results.values() if isinstance(v, dict) and v.get("trait") == "masculine")

    def _count_feminine(self, results) -> int:
        return sum(1 for v in results.values() if isinstance(v, dict) and v.get("trait") == "feminine")

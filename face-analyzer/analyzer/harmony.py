import numpy as np
from typing import Optional


class HarmonyAnalyzer:
    """Analyzes facial proportional balance across 5 harmony dimensions."""

    def __init__(self, detector):
        self.detector = detector

    def analyze(self, landmarks: dict) -> dict:
        """Run all 5 harmony assessments."""
        lm = landmarks["landmarks"]
        d = self.detector.distance

        results = {}

        # 1. Facial Thirds Ratio
        results["facial_thirds"] = self._facial_thirds(lm, d)

        # 2. Facial Fifths Ratio
        results["facial_fifths"] = self._facial_fifths(lm, d)

        # 3. Golden Ratio Adherence
        results["golden_ratio"] = self._golden_ratio(lm, d)

        # 4. Lower Face Third Ratio
        results["lower_face_third"] = self._lower_face_third(lm, d)

        # 5. Eye-to-Mouth Proportion
        results["eye_mouth_proportion"] = self._eye_mouth_proportion(lm, d)

        return results

    def _facial_thirds(self, lm, d) -> dict:
        """Divide face into three equal vertical sections: hairline-nose, nose-mouth, mouth-chin."""
        forehead_top = lm["forehead_top"]
        nose_bottom = lm["nose_bottom"]
        mouth_bottom = lm["mouth_bottom"]
        chin_tip = lm["chin_tip"]

        upper_third = d(forehead_top, nose_bottom) * 0.5
        middle_third = d(nose_bottom, mouth_bottom)
        lower_third = d(mouth_bottom, chin_tip)

        # Ideal: all three roughly equal (ratio ~1.0)
        if middle_third == 0:
            score = 5.0
        else:
            ratios = [upper_third / middle_third, middle_third / lower_third if lower_third > 0 else 1.0]
            avg_deviation = np.mean([abs(r - 1.0) for r in ratios])
            # Score: 10 if perfect, decreases with deviation
            score = max(1.0, min(10.0, 10.0 - avg_deviation * 20))

        return {
            "score": round(score, 1),
            "upper_third": round(upper_third, 1),
            "middle_third": round(middle_third, 1),
            "lower_third": round(lower_third, 1),
            "description": "Balance between forehead, midface, and lower face sections",
        }

    def _facial_fifths(self, lm, d) -> dict:
        """Divide face width into five equal eye-width sections."""
        eye_left_width = d(lm["eye_left_outer"], lm["eye_left_inner"])
        eye_right_width = d(lm["eye_right_outer"], lm["eye_right_inner"])
        interpupillary = d(lm["eye_left_inner"], lm["eye_right_inner"])
        face_width = d(lm["face_left"], lm["face_right"])

        avg_eye_width = (eye_left_width + eye_right_width) / 2
        if avg_eye_width == 0 or face_width == 0:
            score = 5.0
        else:
            # Ideal: face width = 5 * eye width, interpupillary = 1 * eye width
            width_ratio = face_width / (5 * avg_eye_width)
            ipd_ratio = interpupillary / avg_eye_width
            deviation = abs(width_ratio - 1.0) + abs(ipd_ratio - 1.0)
            score = max(1.0, min(10.0, 10.0 - deviation * 10))

        return {
            "score": round(score, 1),
            "face_width_to_eye_ratio": round(face_width / avg_eye_width if avg_eye_width > 0 else 0, 2),
            "interpupillary_to_eye_ratio": round(interpupillary / avg_eye_width if avg_eye_width > 0 else 0, 2),
            "description": "Horizontal spacing: face should be ~5 eye-widths across",
        }

    def _golden_ratio(self, lm, d) -> dict:
        """Check key facial ratios against phi (1.618)."""
        # Key ratios to check
        face_width = d(lm["face_left"], lm["face_right"])
        face_height = d(lm["face_top"], lm["face_bottom"])

        # Width-to-height ratio (ideal ~0.618, inverse of phi)
        wh_ratio = face_width / face_height if face_height > 0 else 0

        # Mouth width to nose width
        mouth_width = d(lm["mouth_left"], lm["mouth_right"])
        nose_width = d(lm["nose_left"], lm["nose_right"])
        mn_ratio = mouth_width / nose_width if nose_width > 0 else 0

        # Eye spacing to eye width
        eye_width = (d(lm["eye_left_outer"], lm["eye_left_inner"]) +
                     d(lm["eye_right_outer"], lm["eye_right_inner"])) / 2
        eye_spacing = d(lm["eye_left_inner"], lm["eye_right_inner"])
        ee_ratio = eye_spacing / eye_width if eye_width > 0 else 0

        phi = 1.618

        # Score based on how close ratios are to golden ratio ideals
        deviations = [
            abs(wh_ratio - 0.618),  # W/H ideal
            abs(mn_ratio - phi) / phi,  # Mouth/nose ideal
            abs(ee_ratio - 1.0),  # Eye spacing ideal
        ]
        avg_deviation = np.mean(deviations)
        score = max(1.0, min(10.0, 10.0 - avg_deviation * 15))

        return {
            "score": round(score, 1),
            "width_height_ratio": round(wh_ratio, 3),
            "mouth_nose_ratio": round(mn_ratio, 2),
            "eye_spacing_ratio": round(ee_ratio, 2),
            "description": "Proximity to golden ratio (1.618) across key measurements",
        }

    def _lower_face_third(self, lm, d) -> dict:
        """Analyze lower face proportions: nose-to-lip vs lip-to-chin."""
        nose_bottom = lm["nose_bottom"]
        lip_top = lm["lip_upper_top"]
        lip_bottom = lm["lip_lower_bottom"]
        chin_tip = lm["chin_tip"]

        nose_to_lip = d(nose_bottom, lip_top)
        lip_to_chin = d(lip_bottom, chin_tip)
        lip_height = d(lip_top, lip_bottom)

        # Ideal: nose-to-lip ~1/3 of lower face, lip-to-chin ~2/3
        lower_face = nose_to_lip + lip_height + lip_to_chin
        if lower_face == 0:
            score = 5.0
        else:
            nose_lip_ratio = nose_to_lip / lower_face
            lip_chin_ratio = lip_to_chin / lower_face
            deviation = abs(nose_lip_ratio - 0.33) + abs(lip_chin_ratio - 0.55)
            score = max(1.0, min(10.0, 10.0 - deviation * 30))

        return {
            "score": round(score, 1),
            "nose_to_lip_pct": round(nose_to_lip / lower_face * 100 if lower_face > 0 else 0, 1),
            "lip_to_chin_pct": round(lip_to_chin / lower_face * 100 if lower_face > 0 else 0, 1),
            "description": "Balance between upper lip area and chin length in lower face",
        }

    def _eye_mouth_proportion(self, lm, d) -> dict:
        """Ratio of eye-level width to mouth-level width."""
        # Width at eye level
        eye_level_width = d(lm["face_left"], lm["face_right"])  # approximated

        # Width at mouth level (cheek to cheek through mouth)
        mouth_level_width = d(lm["cheek_left"], lm["cheek_right"])

        ratio = mouth_level_width / eye_level_width if eye_level_width > 0 else 0

        # Ideal: mouth level slightly narrower than eye level (ratio ~0.85-0.95)
        deviation = abs(ratio - 0.90)
        score = max(1.0, min(10.0, 10.0 - deviation * 25))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Width balance between eye line and mouth line (ideal ~0.90)",
        }

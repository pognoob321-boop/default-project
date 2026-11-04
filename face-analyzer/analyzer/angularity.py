import numpy as np
from typing import Optional


class AngularityAnalyzer:
    """Analyzes jawline and bone structure definition across 12 measurements."""

    def __init__(self, detector):
        self.detector = detector

    def analyze(self, landmarks: dict) -> dict:
        """Run all 12 angularity measurements."""
        lm = landmarks["landmarks"]
        d = self.detector.distance
        angle = self.detector.angle_between

        results = {}

        # 1. Gonial Angle (jaw angle)
        results["gonial_angle"] = self._gonial_angle(lm, angle)

        # 2. Jawline Definition
        results["jawline_definition"] = self._jawline_definition(lm, d)

        # 3. Chin Projection
        results["chin_projection"] = self._chin_projection(lm, d)

        # 4. Chin Width
        results["chin_width"] = self._chin_width(lm, d)

        # 5. Cheekbone Width (bizygomatic)
        results["bizygomatic_width"] = self._bizygomatic_width(lm, d)

        # 6. Midface Height Ratio
        results["midface_height"] = self._midface_height(lm, d)

        # 7. Lower Face Height Ratio
        results["lower_face_height"] = self._lower_face_height(lm, d)

        # 8. Mandible Length
        results["mandible_length"] = self._mandible_length(lm, d)

        # 9. Ramus Height
        results["ramus_height"] = self._ramus_height(lm, d)

        # 10. Bigonial Width
        results["bigonial_width"] = self._bigonial_width(lm, d)

        # 11. Facial Width-to-Height Ratio
        results["facial_wh_ratio"] = self._facial_wh_ratio(lm, d)

        # 12. Jaw Slope Angle
        results["jaw_slope"] = self._jaw_slope(lm, angle)

        return results

    def _gonial_angle(self, lm, angle) -> dict:
        """Angle formed at the jaw corner — key bone structure indicator."""
        # Approximate gonial angle using jaw landmarks
        # Left side: ramus meets mandible body
        angle_val = angle(lm["jaw_left_top"], lm["jaw_left_mid"], lm["chin_left"])

        # Ideal: ~120-130 degrees for masculine, ~125-135 for feminine
        # Score: closest to 125 gets highest score
        deviation = abs(angle_val - 125) / 125
        score = max(1.0, min(10.0, 10.0 - deviation * 30))

        return {
            "score": round(score, 1),
            "value": round(angle_val, 1),
            "unit": "degrees",
            "ideal_range": "120-130",
            "description": "Jaw corner angle — sharper angles = more defined jawline",
        }

    def _jawline_definition(self, lm, d) -> dict:
        """Sharpness/clarity of jawline edge."""
        # Measure distance from jawline to neck region (sharp = large distance gradient)
        jaw_left = lm["jaw_left_mid"]
        jaw_right = lm["jaw_right_mid"]
        chin = lm["chin_tip"]

        # Jawline length
        left_jaw_length = d(jaw_left, chin)
        right_jaw_length = d(jaw_right, chin)
        jaw_symmetry = 1.0 - abs(left_jaw_length - right_jaw_length) / max(left_jaw_length, right_jaw_length, 1)

        # Jaw width relative to face width
        jaw_width = d(jaw_left, jaw_right)
        face_width = d(lm["face_left"], lm["face_right"])
        jaw_face_ratio = jaw_width / face_width if face_width > 0 else 0

        # Ideal: jaw ~65-80% of face width, high symmetry
        ratio_score = 10.0 - abs(jaw_face_ratio - 0.72) * 25
        symmetry_score = jaw_symmetry * 10

        score = (ratio_score + symmetry_score) / 2
        score = max(1.0, min(10.0, score))

        return {
            "score": round(score, 1),
            "jaw_face_ratio": round(jaw_face_ratio, 3),
            "symmetry": round(jaw_symmetry, 3),
            "description": "Jawline clarity and definition relative to face width",
        }

    def _chin_projection(self, lm, d) -> dict:
        """How far the chin projects forward."""
        nose_tip = lm["nose_tip"]
        chin = lm["chin_tip"]
        lip_bottom = lm["lip_lower_bottom"]

        # Chin projection: distance from nose tip to chin vertical
        chin_projection = d(nose_tip, chin)
        face_height = d(lm["face_top"], lm["face_bottom"])

        ratio = chin_projection / face_height if face_height > 0 else 0

        # Ideal: chin projects ~20-25% of face height
        deviation = abs(ratio - 0.22)
        score = max(1.0, min(10.0, 10.0 - deviation * 40))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Forward chin projection relative to face height",
        }

    def _chin_width(self, lm, d) -> dict:
        """Width of the chin area."""
        chin_left = lm["chin_left"]
        chin_right = lm["chin_right"]
        chin_tip = lm["chin_tip"]

        chin_w = d(chin_left, chin_right)
        face_w = d(lm["face_left"], lm["face_right"])

        ratio = chin_w / face_w if face_w > 0 else 0

        # Ideal: chin ~25-35% of face width
        deviation = abs(ratio - 0.30)
        score = max(1.0, min(10.0, 10.0 - deviation * 25))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Chin width relative to overall face width",
        }

    def _bizygomatic_width(self, lm, d) -> dict:
        """Width across the cheekbones (zygomatic arches)."""
        left_cheek = lm["cheek_left"]
        right_cheek = lm["cheek_right"]

        bizyg = d(left_cheek, right_cheek)
        face_w = d(lm["face_left"], lm["face_right"])

        ratio = bizyg / face_w if face_w > 0 else 0

        # Ideal: cheekbone width should be close to face width (0.95-1.0)
        deviation = abs(ratio - 0.97)
        score = max(1.0, min(10.0, 10.0 - deviation * 20))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "absolute": round(bizyg, 1),
            "description": "Cheekbone width — prominent cheekbones score higher",
        }

    def _midface_height(self, lm, d) -> dict:
        """Height of the midface (brow to nose bottom)."""
        brow_center = lm["brow_left_inner"]  # approx brow level
        nose_bottom = lm["nose_bottom"]
        face_height = d(lm["face_top"], lm["face_bottom"])

        midface_h = d(brow_center, nose_bottom)
        ratio = midface_h / face_height if face_height > 0 else 0

        # Ideal: midface ~33-38% of total face height
        deviation = abs(ratio - 0.35)
        score = max(1.0, min(10.0, 10.0 - deviation * 25))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Midface height relative to total face height",
        }

    def _lower_face_height(self, lm, d) -> dict:
        """Height from nose bottom to chin."""
        nose_bottom = lm["nose_bottom"]
        chin = lm["chin_tip"]
        face_height = d(lm["face_top"], lm["face_bottom"])

        lower_h = d(nose_bottom, chin)
        ratio = lower_h / face_height if face_height > 0 else 0

        # Ideal: lower face ~33-40% of total face height
        deviation = abs(ratio - 0.36)
        score = max(1.0, min(10.0, 10.0 - deviation * 20))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Lower face height (nose to chin) relative to total face",
        }

    def _mandible_length(self, lm, d) -> dict:
        """Length of the mandible jawbone."""
        jaw_left_top = lm["jaw_left_top"]
        jaw_right_top = lm["jaw_right_top"]
        chin = lm["chin_tip"]

        left_mandible = d(jaw_left_top, chin)
        right_mandible = d(jaw_right_top, chin)
        avg_mandible = (left_mandible + right_mandible) / 2

        face_height = d(lm["face_top"], lm["face_bottom"])
        ratio = avg_mandible / face_height if face_height > 0 else 0

        # Longer mandible relative to face = more angular
        # Ideal ratio ~0.55-0.65
        deviation = abs(ratio - 0.60)
        score = max(1.0, min(10.0, 10.0 - deviation * 20))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "symmetry": round(1.0 - abs(left_mandible - right_mandible) / max(left_mandible, right_mandible, 1), 3),
            "description": "Jawbone length relative to face height",
        }

    def _ramus_height(self, lm, d) -> dict:
        """Height of the mandibular ramus (vertical jaw segment)."""
        jaw_top = lm["jaw_left_top"]
        jaw_mid = lm["jaw_left_mid"]

        ramus = d(jaw_top, jaw_mid)
        face_height = d(lm["face_top"], lm["face_bottom"])

        ratio = ramus / face_height if face_height > 0 else 0

        # Ideal ramus ~20-25% of face height
        deviation = abs(ratio - 0.22)
        score = max(1.0, min(10.0, 10.0 - deviation * 30))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Vertical jaw segment height — longer ramus = more defined jaw",
        }

    def _bigonial_width(self, lm, d) -> dict:
        """Width at the jaw angle (bigonial width)."""
        jaw_left = lm["jaw_left_bottom"]
        jaw_right = lm["jaw_right_bottom"]

        bigonial = d(jaw_left, jaw_right)
        face_w = d(lm["face_left"], lm["face_right"])

        ratio = bigonial / face_w if face_w > 0 else 0

        # Ideal: bigonial ~60-75% of face width
        deviation = abs(ratio - 0.68)
        score = max(1.0, min(10.0, 10.0 - deviation * 20))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Width at jaw angle — wider = more angular appearance",
        }

    def _facial_wh_ratio(self, lm, d) -> dict:
        """Facial width-to-height ratio — key attractiveness metric."""
        face_w = d(lm["face_left"], lm["face_right"])
        face_h = d(lm["face_top"], lm["face_bottom"])

        ratio = face_w / face_h if face_h > 0 else 0

        # Ideal W/H ratio ~0.75-0.85
        deviation = abs(ratio - 0.80)
        score = max(1.0, min(10.0, 10.0 - deviation * 20))

        return {
            "score": round(score, 1),
            "ratio": round(ratio, 3),
            "description": "Face width divided by height — key proportionality metric",
        }

    def _jaw_slope(self, lm, angle) -> dict:
        """Angle of the jawline from horizontal."""
        jaw_left = lm["jaw_left_mid"]
        chin = lm["chin_tip"]

        # Create a horizontal reference point
        horizontal = np.array([chin[0] - 100, chin[1]], dtype=np.float64)
        slope_angle = angle(jaw_left, chin, horizontal)

        # Ideal: ~20-30 degrees from horizontal
        deviation = abs(slope_angle - 25) / 25
        score = max(1.0, min(10.0, 10.0 - deviation * 15))

        return {
            "score": round(score, 1),
            "value": round(slope_angle, 1),
            "unit": "degrees",
            "description": "Jawline slope from horizontal — steeper = more angular",
        }

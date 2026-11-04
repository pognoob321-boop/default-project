import numpy as np
import cv2
from typing import Optional


class HealthAnalyzer:
    """Analyzes skin health, symmetry, and feature-level indicators (40+ metrics)."""

    def __init__(self, detector):
        self.detector = detector

    def analyze(self, landmarks: dict, image_path: str = None) -> dict:
        """Run comprehensive health indicator analysis."""
        lm = landmarks["landmarks"]
        raw = landmarks["raw_landmarks"]
        d = self.detector.distance

        results = {}

        # A. Symmetry Metrics (10)
        results["symmetry"] = self._symmetry_analysis(lm, d)

        # B. Eye Area Metrics (8)
        results["eye_area"] = self._eye_area_analysis(lm, d)

        # C. Skin Metrics (from image if available)
        if image_path:
            results["skin"] = self._skin_analysis(image_path, lm)
        else:
            results["skin"] = {"note": "Image not provided for skin analysis"}

        # D. Nose Metrics (5)
        results["nose"] = self._nose_analysis(lm, d)

        # E. Mouth & Lip Metrics (5)
        results["mouth"] = self._mouth_analysis(lm, d)

        # F. Brow Metrics (5)
        results["brows"] = self._brow_analysis(lm, d)

        # G. Facial Proportion Health Indicators (7+)
        results["proportions"] = self._proportion_health(lm, d)

        # H. Age Indicators
        results["age_indicators"] = self._age_indicators(lm, d)

        # Overall health score
        all_scores = []
        for category in results.values():
            if isinstance(category, dict):
                for k, v in category.items():
                    if isinstance(v, dict) and "score" in v:
                        all_scores.append(v["score"])

        results["overall_health"] = {
            "score": round(np.mean(all_scores), 1) if all_scores else 5.0,
            "total_metrics": len(all_scores),
            "description": "Composite health indicator across all sub-categories",
        }

        return results

    def _symmetry_analysis(self, lm, d) -> dict:
        """Left-right facial symmetry across multiple dimensions."""
        results = {}

        # 1. Eye symmetry
        left_eye_w = d(lm["eye_left_outer"], lm["eye_left_inner"])
        right_eye_w = d(lm["eye_right_outer"], lm["eye_right_inner"])
        eye_sym = 1.0 - abs(left_eye_w - right_eye_w) / max(left_eye_w, right_eye_w, 1)
        results["eye_symmetry"] = {
            "score": round(eye_sym * 10, 1),
            "left_width": round(left_eye_w, 1),
            "right_width": round(right_eye_w, 1),
            "description": "Left-right eye width balance",
        }

        # 2. Brow symmetry
        left_brow_h = d(lm["brow_left_inner"], lm["brow_left_outer"])
        right_brow_h = d(lm["brow_right_inner"], lm["brow_right_outer"])
        brow_sym = 1.0 - abs(left_brow_h - right_brow_h) / max(left_brow_h, right_brow_h, 1)
        results["brow_symmetry"] = {
            "score": round(brow_sym * 10, 1),
            "description": "Left-right eyebrow length balance",
        }

        # 3. Mouth symmetry
        mouth_center_x = (lm["mouth_left"][0] + lm["mouth_right"][0]) / 2
        nose_center_x = (lm["nose_left"][0] + lm["nose_right"][0]) / 2
        mouth_offset = abs(mouth_center_x - nose_center_x) / d(lm["face_left"], lm["face_right"])
        mouth_sym = max(0, 1.0 - mouth_offset * 10)
        results["mouth_symmetry"] = {
            "score": round(mouth_sym * 10, 1),
            "offset_pct": round(mouth_offset * 100, 1),
            "description": "Mouth centering relative to nose",
        }

        # 4. Jaw symmetry
        left_jaw = d(lm["jaw_left_mid"], lm["chin_tip"])
        right_jaw = d(lm["jaw_right_mid"], lm["chin_tip"])
        jaw_sym = 1.0 - abs(left_jaw - right_jaw) / max(left_jaw, right_jaw, 1)
        results["jaw_symmetry"] = {
            "score": round(jaw_sym * 10, 1),
            "description": "Left-right jawline balance",
        }

        # 5. Cheekbone symmetry
        left_cheek_dist = d(lm["cheek_left"], lm["eye_left_inner"])
        right_cheek_dist = d(lm["cheek_right"], lm["eye_right_inner"])
        cheek_sym = 1.0 - abs(left_cheek_dist - right_cheek_dist) / max(left_cheek_dist, right_cheek_dist, 1)
        results["cheekbone_symmetry"] = {
            "score": round(cheek_sym * 10, 1),
            "description": "Left-right cheekbone prominence balance",
        }

        # 6. Nose deviation
        nose_center_x = (lm["nose_left"][0] + lm["nose_right"][0]) / 2
        face_center_x = (lm["face_left"][0] + lm["face_right"][0]) / 2
        nose_deviation = abs(nose_center_x - face_center_x) / d(lm["face_left"], lm["face_right"])
        nose_sym = max(0, 1.0 - nose_deviation * 15)
        results["nose_symmetry"] = {
            "score": round(nose_sym * 10, 1),
            "deviation_pct": round(nose_deviation * 100, 1),
            "description": "Nose centering relative to face midline",
        }

        # 7. Overall facial symmetry (composite)
        sym_scores = [v["score"] for v in results.values() if "score" in v]
        results["overall_symmetry"] = {
            "score": round(np.mean(sym_scores), 1),
            "description": "Composite left-right facial symmetry",
        }

        return results

    def _eye_area_analysis(self, lm, d) -> dict:
        """Eye area health and aesthetics."""
        results = {}

        # 1. Canthal tilt (eye angle)
        left_outer = lm["eye_left_outer"]
        left_inner = lm["eye_left_inner"]
        right_outer = lm["eye_right_outer"]
        right_inner = lm["eye_right_inner"]

        # Approximate canthal tilt
        left_tilt = (left_outer[1] - left_inner[1]) / max(d(left_outer, left_inner), 1)
        right_tilt = (right_outer[1] - right_inner[1]) / max(d(right_outer, right_inner), 1)
        avg_tilt = (left_tilt + right_tilt) / 2

        # Positive tilt (outer corner higher) = ideal
        tilt_score = 5.0 + avg_tilt * 20
        tilt_score = max(1.0, min(10.0, tilt_score))
        results["canthal_tilt"] = {
            "score": round(tilt_score, 1),
            "value": round(avg_tilt, 3),
            "description": "Eye angle — positive tilt (outer corners higher) is ideal",
        }

        # 2. Eye openness
        left_open = d(lm["eye_left_top"], lm["eye_left_bottom"])
        right_open = d(lm["eye_right_top"], lm["eye_right_bottom"])
        avg_open = (left_open + right_open) / 2
        eye_w = (d(lm["eye_left_outer"], lm["eye_left_inner"]) +
                 d(lm["eye_right_outer"], lm["eye_right_inner"])) / 2
        openness_ratio = avg_open / eye_w if eye_w > 0 else 0

        # Ideal openness ~0.35-0.45
        open_score = 10.0 - abs(openness_ratio - 0.40) * 25
        open_score = max(1.0, min(10.0, open_score))
        results["eye_openness"] = {
            "score": round(open_score, 1),
            "ratio": round(openness_ratio, 3),
            "description": "Eye openness relative to width",
        }

        # 3. Eye spacing (interpupillary distance)
        ipd = d(lm["eye_left_inner"], lm["eye_right_inner"])
        face_w = d(lm["face_left"], lm["face_right"])
        ipd_ratio = ipd / face_w if face_w > 0 else 0

        # Ideal IPD ~0.46 of face width
        ipd_score = 10.0 - abs(ipd_ratio - 0.46) * 25
        ipd_score = max(1.0, min(10.0, ipd_score))
        results["eye_spacing"] = {
            "score": round(ipd_score, 1),
            "ratio": round(ipd_ratio, 3),
            "description": "Eye spacing relative to face width",
        }

        # 4. Under-eye area (distance from lower eyelid to cheek)
        eye_bottom = lm["eye_left_bottom"]
        cheek = lm["cheek_left"]
        under_eye = d(eye_bottom, cheek)
        eye_h = d(lm["eye_left_top"], lm["eye_left_bottom"])
        under_ratio = under_eye / eye_h if eye_h > 0 else 0

        # Lower ratio = less under-eye hollow
        under_score = 10.0 - under_ratio * 5
        under_score = max(1.0, min(10.0, under_score))
        results["under_eye"] = {
            "score": round(under_score, 1),
            "ratio": round(under_ratio, 3),
            "description": "Under-eye area — lower ratio suggests less hollowness",
        }

        # 5. Eye size uniformity
        left_area = d(lm["eye_left_outer"], lm["eye_left_inner"]) * d(lm["eye_left_top"], lm["eye_left_bottom"])
        right_area = d(lm["eye_right_outer"], lm["eye_right_inner"]) * d(lm["eye_right_top"], lm["eye_right_bottom"])
        size_ratio = min(left_area, right_area) / max(left_area, right_area, 1)
        results["eye_size_uniformity"] = {
            "score": round(size_ratio * 10, 1),
            "ratio": round(size_ratio, 3),
            "description": "Left-right eye size consistency",
        }

        return results

    def _skin_analysis(self, image_path: str, lm: dict) -> dict:
        """Analyze skin quality from the actual image."""
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Could not load image"}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, w = img.shape[:2]

        results = {}

        # 1. Skin uniformity (brightness variance in face region)
        # Create face mask from key landmarks
        face_pts = np.array([
            [int(lm["face_left"][0]), int(lm["face_left"][1])],
            [int(lm["forehead_top"][0]), int(lm["forehead_top"][1])],
            [int(lm["face_right"][0]), int(lm["face_right"][1])],
            [int(lm["chin_tip"][0]), int(lm["chin_tip"][1])],
        ], dtype=np.int32)

        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.fillPoly(mask, [face_pts], 255)

        face_pixels = gray[mask > 0]
        if len(face_pixels) > 0:
            brightness_std = np.std(face_pixels)
            uniformity = max(0, 1.0 - brightness_std / 60)
            results["skin_uniformity"] = {
                "score": round(uniformity * 10, 1),
                "std_dev": round(brightness_std, 1),
                "description": "Evenness of skin tone across face",
            }

        # 2. Skin smoothness (texture via Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        face_lap = laplacian[mask > 0]
        texture_var = np.var(face_lap) if len(face_lap) > 0 else 0
        # Lower variance = smoother skin
        smoothness = max(0, min(10, 10.0 - texture_var / 500))
        results["skin_smoothness"] = {
            "score": round(smoothness, 1),
            "texture_variance": round(texture_var, 1),
            "description": "Skin texture smoothness (lower texture variance = smoother)",
        }

        # 3. Dark circle detection (under-eye region)
        # Approximate under-eye region
        left_eye_center = ((lm["eye_left_inner"][0] + lm["eye_left_outer"][0]) / 2,
                           (lm["eye_left_top"][1] + lm["eye_left_bottom"][1]) / 2)
        right_eye_center = ((lm["eye_right_inner"][0] + lm["eye_right_outer"][0]) / 2,
                            (lm["eye_right_top"][1] + lm["eye_right_bottom"][1]) / 2)

        # Sample under-eye region (below eye, above cheek)
        for side, eye_c in [("left", left_eye_center), ("right", right_eye_center)]:
            y_start = int(eye_c[1])
            y_end = min(int(eye_c[1] + (lm["cheek_left"][1] - eye_c[1]) * 0.3), h)
            x_start = max(int(eye_c[0] - 30), 0)
            x_end = min(int(eye_c[0] + 30), w)

            if y_end > y_start and x_end > x_start:
                region = hsv[y_start:y_end, x_start:x_end]
                if len(region) > 0:
                    avg_value = np.mean(region[:, :, 2])
                    # Darker under-eyes = lower value
                    dark_score = max(1.0, min(10.0, avg_value / 25.5))
                    results[f"dark_circles_{side}"] = {
                        "score": round(dark_score, 1),
                        "brightness": round(avg_value, 1),
                        "description": f"Under-eye brightness ({side})",
                    }

        # 4. Forehead smoothness
        forehead_y = int(lm["forehead_top"][1])
        forehead_x_left = int(lm["forehead_left"][0])
        forehead_x_right = int(lm["forehead_right"][0])
        if forehead_x_right > forehead_x_left and forehead_y + 40 < h:
            forehead_region = gray[forehead_y:forehead_y+40, forehead_x_left:forehead_x_right]
            if len(forehead_region) > 0:
                f_lap = cv2.Laplacian(forehead_region, cv2.CV_64F)
                f_var = np.var(f_lap)
                f_smooth = max(0, min(10, 10.0 - f_var / 300))
                results["forehead_smoothness"] = {
                    "score": round(f_smooth, 1),
                    "description": "Smoothness of forehead skin",
                }

        # 5. Overall skin health (composite)
        skin_scores = [v["score"] for v in results.values() if "score" in v and isinstance(v, dict)]
        results["overall_skin"] = {
            "score": round(np.mean(skin_scores), 1) if skin_scores else 5.0,
            "description": "Composite skin health score",
        }

        return results

    def _nose_analysis(self, lm, d) -> dict:
        """Nose feature analysis."""
        results = {}

        # 1. Nose width ratio
        nose_w = d(lm["nose_left"], lm["nose_right"])
        face_w = d(lm["face_left"], lm["face_right"])
        nose_ratio = nose_w / face_w if face_w > 0 else 0
        nose_score = 10.0 - abs(nose_ratio - 0.18) * 30
        nose_score = max(1.0, min(10.0, nose_score))
        results["nose_width_ratio"] = {
            "score": round(nose_score, 1),
            "ratio": round(nose_ratio, 3),
            "description": "Nose width relative to face width",
        }

        # 2. Nose projection
        nose_tip = lm["nose_tip"]
        nose_bridge = lm["nose_bridge_top"]
        nose_h = d(nose_bridge, nose_tip)
        nose_proj_ratio = nose_h / face_w if face_w > 0 else 0
        proj_score = 10.0 - abs(nose_proj_ratio - 0.15) * 30
        proj_score = max(1.0, min(10.0, proj_score))
        results["nose_projection"] = {
            "score": round(proj_score, 1),
            "ratio": round(nose_proj_ratio, 3),
            "description": "Nose projection relative to face width",
        }

        # 3. Nose length ratio
        face_h = d(lm["face_top"], lm["face_bottom"])
        nose_length_ratio = nose_h / face_h if face_h > 0 else 0
        len_score = 10.0 - abs(nose_length_ratio - 0.33) * 20
        len_score = max(1.0, min(10.0, len_score))
        results["nose_length"] = {
            "score": round(len_score, 1),
            "ratio": round(nose_length_ratio, 3),
            "description": "Nose length relative to face height",
        }

        # 4. Nostril symmetry
        nostril_left = lm["nose_nostril_left"]
        nostril_right = lm["nose_nostril_right"]
        nostril_sym = 1.0 - abs(nostril_left[1] - nostril_right[1]) / max(d(nostril_left, nostril_right), 1)
        results["nostril_symmetry"] = {
            "score": round(max(0, nostril_sym) * 10, 1),
            "description": "Left-right nostril height balance",
        }

        # 5. Nasolabial angle
        naso_angle = self.detector.angle_between(lm["nose_bridge_mid"], lm["nose_tip"], lm["lip_upper_top"])
        angle_score = 10.0 - abs(naso_angle - 105) / 10
        angle_score = max(1.0, min(10.0, angle_score))
        results["nasolabial_angle"] = {
            "score": round(angle_score, 1),
            "value": round(naso_angle, 1),
            "description": "Angle between nose and upper lip",
        }

        return results

    def _mouth_analysis(self, lm, d) -> dict:
        """Mouth and lip feature analysis."""
        results = {}

        # 1. Mouth width ratio
        mouth_w = d(lm["mouth_left"], lm["mouth_right"])
        face_w = d(lm["face_left"], lm["face_right"])
        mouth_ratio = mouth_w / face_w if face_w > 0 else 0
        m_score = 10.0 - abs(mouth_ratio - 0.38) * 20
        m_score = max(1.0, min(10.0, m_score))
        results["mouth_width"] = {
            "score": round(m_score, 1),
            "ratio": round(mouth_ratio, 3),
            "description": "Mouth width relative to face width",
        }

        # 2. Lip ratio (upper to lower)
        upper_h = d(lm["lip_upper_top"], lm["lip_upper_mid"])
        lower_h = d(lm["lip_lower_mid"], lm["lip_lower_bottom"])
        lip_ratio = upper_h / lower_h if lower_h > 0 else 1.0
        lr_score = 10.0 - abs(lip_ratio - 0.67) * 15
        lr_score = max(1.0, min(10.0, lr_score))
        results["lip_proportion"] = {
            "score": round(lr_score, 1),
            "ratio": round(lip_ratio, 3),
            "description": "Upper-to-lower lip height ratio (ideal ~0.67)",
        }

        # 3. Mouth corner position (smile line)
        mouth_left_y = lm["mouth_left"][1]
        mouth_right_y = lm["mouth_right"][1]
        mouth_center_y = (mouth_left_y + mouth_right_y) / 2
        lip_bottom_y = lm["lip_lower_bottom"][1]
        upturn = (mouth_left_y + mouth_right_y) / 2 - lip_bottom_y
        face_h = d(lm["face_top"], lm["face_bottom"])
        upturn_ratio = upturn / face_h if face_h > 0 else 0
        uc_score = 5.0 + upturn_ratio * 50
        uc_score = max(1.0, min(10.0, uc_score))
        results["mouth_corners"] = {
            "score": round(uc_score, 1),
            "description": "Mouth corner upturn — slight upturn is positive",
        }

        # 4. Philtrum length
        nose_bottom = lm["nose_bottom"]
        lip_top = lm["lip_upper_top"]
        philtrum = d(nose_bottom, lip_top)
        phil_ratio = philtrum / face_h if face_h > 0 else 0
        ph_score = 10.0 - abs(phil_ratio - 0.10) * 40
        ph_score = max(1.0, min(10.0, ph_score))
        results["philtrum"] = {
            "score": round(ph_score, 1),
            "ratio": round(phil_ratio, 3),
            "description": "Philtrum length relative to face height",
        }

        # 5. Lip symmetry
        lip_center_x = (lm["mouth_left"][0] + lm["mouth_right"][0]) / 2
        nose_center_x = (lm["nose_left"][0] + lm["nose_right"][0]) / 2
        lip_offset = abs(lip_center_x - nose_center_x) / face_w
        lip_sym = max(0, 1.0 - lip_offset * 10)
        results["lip_symmetry"] = {
            "score": round(lip_sym * 10, 1),
            "description": "Left-right lip balance",
        }

        return results

    def _brow_analysis(self, lm, d) -> dict:
        """Eyebrow feature analysis."""
        results = {}

        # 1. Brow length
        left_brow = d(lm["brow_left_inner"], lm["brow_left_outer"])
        right_brow = d(lm["brow_right_inner"], lm["brow_right_outer"])
        avg_brow = (left_brow + right_brow) / 2
        eye_w = (d(lm["eye_left_outer"], lm["eye_left_inner"]) +
                 d(lm["eye_right_outer"], lm["eye_right_inner"])) / 2
        brow_eye_ratio = avg_brow / eye_w if eye_w > 0 else 1.0
        bl_score = 10.0 - abs(brow_eye_ratio - 1.3) * 10
        bl_score = max(1.0, min(10.0, bl_score))
        results["brow_length"] = {
            "score": round(bl_score, 1),
            "ratio": round(brow_eye_ratio, 3),
            "description": "Brow length relative to eye width",
        }

        # 2. Brow arch height
        brow_inner = lm["brow_left_inner"]
        brow_mid = lm["brow_left_mid"]
        brow_outer = lm["brow_left_outer"]
        arch_height = brow_inner[1] - brow_mid[1]  # positive = arched
        brow_length = d(brow_inner, brow_outer)
        arch_ratio = arch_height / brow_length if brow_length > 0 else 0
        arch_score = 5.0 + arch_ratio * 20
        arch_score = max(1.0, min(10.0, arch_score))
        results["brow_arch"] = {
            "score": round(arch_score, 1),
            "ratio": round(arch_ratio, 3),
            "description": "Brow arch height — moderate arch is ideal",
        }

        # 3. Brow thickness consistency
        brow_top = lm["brow_left_mid"]
        # Approximate brow thickness
        brow_thickness = abs(brow_top[1] - lm["brow_left_inner"][1])
        face_h = d(lm["face_top"], lm["face_bottom"])
        thickness_ratio = brow_thickness / face_h if face_h > 0 else 0
        bt_score = 10.0 - abs(thickness_ratio - 0.02) * 100
        bt_score = max(1.0, min(10.0, bt_score))
        results["brow_thickness"] = {
            "score": round(bt_score, 1),
            "ratio": round(thickness_ratio, 4),
            "description": "Brow thickness relative to face height",
        }

        # 4. Brow spacing
        inner_dist = d(lm["brow_left_inner"], lm["brow_right_inner"])
        ipd = d(lm["eye_left_inner"], lm["eye_right_inner"])
        spacing_ratio = inner_dist / ipd if ipd > 0 else 1.0
        bs_score = 10.0 - abs(spacing_ratio - 1.0) * 15
        bs_score = max(1.0, min(10.0, bs_score))
        results["brow_spacing"] = {
            "score": round(bs_score, 1),
            "ratio": round(spacing_ratio, 3),
            "description": "Distance between inner brow corners",
        }

        # 5. Brow symmetry (vertical position)
        left_y = lm["brow_left_mid"][1]
        right_y = lm["brow_right_mid"][1]
        brow_vert_sym = 1.0 - abs(left_y - right_y) / d(lm["face_left"], lm["face_right"])
        results["brow_vertical_symmetry"] = {
            "score": round(max(0, brow_vert_sym) * 10, 1),
            "description": "Left-right brow height balance",
        }

        return results

    def _proportion_health(self, lm, d) -> dict:
        """Additional proportion-based health indicators."""
        results = {}

        # 1. Face width-to-height ratio
        fw = d(lm["face_left"], lm["face_right"])
        fh = d(lm["face_top"], lm["face_bottom"])
        fwh = fw / fh if fh > 0 else 0
        fwh_score = 10.0 - abs(fwh - 0.80) * 20
        fwh_score = max(1.0, min(10.0, fwh_score))
        results["face_wh_ratio"] = {
            "score": round(fwh_score, 1),
            "ratio": round(fwh, 3),
            "description": "Overall face width-to-height ratio",
        }

        # 2. Eye-to-nose distance ratio
        eye_nose = d(lm["eye_left_inner"], lm["nose_bridge_top"])
        face_h = d(lm["face_top"], lm["face_bottom"])
        en_ratio = eye_nose / face_h if face_h > 0 else 0
        en_score = 10.0 - abs(en_ratio - 0.12) * 30
        en_score = max(1.0, min(10.0, en_score))
        results["eye_nose_distance"] = {
            "score": round(en_score, 1),
            "ratio": round(en_ratio, 3),
            "description": "Distance between inner eye and nose bridge",
        }

        # 3. Ear-to-eye ratio (approximated via jaw width)
        jaw_w = d(lm["jaw_left_top"], lm["jaw_right_top"])
        eye_level_w = fw
        jaw_eye_ratio = jaw_w / eye_level_w if eye_level_w > 0 else 1.0
        je_score = 10.0 - abs(jaw_eye_ratio - 0.70) * 15
        je_score = max(1.0, min(10.0, je_score))
        results["jaw_to_eye_ratio"] = {
            "score": round(je_score, 1),
            "ratio": round(jaw_eye_ratio, 3),
            "description": "Jaw width at eye level relative to face width",
        }

        # 4. Facial convexity
        nose_tip = lm["nose_tip"]
        lip = lm["lip_upper_mid"]
        chin = lm["chin_tip"]
        # Angle: brow-nose tip-chin
        convex_angle = self.detector.angle_between(
            lm["nose_bridge_top"], nose_tip, chin
        )
        cv_score = 10.0 - abs(convex_angle - 170) / 5
        cv_score = max(1.0, min(10.0, cv_score))
        results["facial_convexity"] = {
            "score": round(cv_score, 1),
            "angle": round(convex_angle, 1),
            "description": "Facial profile convexity angle",
        }

        # 5. Lower face ratio
        nose_to_mouth = d(lm["nose_bottom"], lm["mouth_top"])
        mouth_to_chin = d(lm["mouth_bottom"], lm["chin_tip"])
        lower_ratio = nose_to_mouth / mouth_to_chin if mouth_to_chin > 0 else 1.0
        lr_score = 10.0 - abs(lower_ratio - 0.50) * 15
        lr_score = max(1.0, min(10.0, lr_score))
        results["lower_face_balance"] = {
            "score": round(lr_score, 1),
            "ratio": round(lower_ratio, 3),
            "description": "Nose-to-mouth vs mouth-to-chin balance",
        }

        # 6. Midface ratio
        midface_h = d(lm["brow_left_inner"], lm["nose_bottom"])
        midface_w = d(lm["cheek_left"], lm["cheek_right"])
        mid_ratio = midface_h / midface_w if midface_w > 0 else 1.0
        mf_score = 10.0 - abs(mid_ratio - 0.60) * 15
        mf_score = max(1.0, min(10.0, mf_score))
        results["midface_ratio"] = {
            "score": round(mf_score, 1),
            "ratio": round(mid_ratio, 3),
            "description": "Midface height-to-width ratio",
        }

        # 7. Eye-to-chin ratio
        eye_chin = d(lm["eye_left_inner"], lm["chin_tip"])
        face_h = d(lm["face_top"], lm["face_bottom"])
        ec_ratio = eye_chin / face_h if face_h > 0 else 1.0
        ec_score = 10.0 - abs(ec_ratio - 0.65) * 15
        ec_score = max(1.0, min(10.0, ec_score))
        results["eye_to_chin_ratio"] = {
            "score": round(ec_score, 1),
            "ratio": round(ec_ratio, 3),
            "description": "Eye level to chin distance relative to face height",
        }

        return results

    def _age_indicators(self, lm, d) -> dict:
        """Facial features associated with perceived age."""
        results = {}

        # 1. Midface volume (fullness = youthful)
        cheek_left = lm["cheek_left"]
        cheek_right = lm["cheek_right"]
        eye_bottom = lm["eye_left_bottom"]
        cheek_to_eye = d(cheek_left, eye_bottom)
        face_h = d(lm["face_top"], lm["face_bottom"])
        volume_ratio = cheek_to_eye / face_h if face_h > 0 else 0
        vol_score = 5.0 + (0.15 - volume_ratio) * 30
        vol_score = max(1.0, min(10.0, vol_score))
        results["midface_volume"] = {
            "score": round(vol_score, 1),
            "ratio": round(volume_ratio, 3),
            "description": "Midface fullness — fuller = more youthful appearance",
        }

        # 2. Under-eye area
        eye_bottom_y = lm["eye_left_bottom"][1]
        cheek_y = lm["cheek_left"][1]
        under_eye_dist = (cheek_y - eye_bottom_y) / face_h if face_h > 0 else 0
        ue_score = 10.0 - under_eye_dist * 30
        ue_score = max(1.0, min(10.0, ue_score))
        results["under_eye_area"] = {
            "score": round(ue_score, 1),
            "description": "Under-eye region — less hollow = more youthful",
        }

        # 3. Jawline definition (sharp = youthful)
        jaw_left = lm["jaw_left_mid"]
        jaw_right = lm["jaw_right_mid"]
        chin = lm["chin_tip"]
        jaw_length = d(jaw_left, jaw_right)
        chin_length = d(chin, lm["lip_lower_bottom"])
        jaw_chin_ratio = jaw_length / chin_length if chin_length > 0 else 1.0
        jc_score = 5.0 + (jaw_chin_ratio - 2.0) * 3
        jc_score = max(1.0, min(10.0, jc_score))
        results["jawline_youth"] = {
            "score": round(jc_score, 1),
            "ratio": round(jaw_chin_ratio, 3),
            "description": "Jawline definition — sharper = more youthful",
        }

        return results

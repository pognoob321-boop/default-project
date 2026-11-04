import numpy as np
from typing import Optional


class ScoringEngine:
    """Combines all four pillars into overall and pillar-level scores."""

    PILLAR_WEIGHTS = {
        "harmony": 0.30,
        "angularity": 0.25,
        "dimorphism": 0.15,
        "health": 0.30,
    }

    def compute_scores(self, harmony: dict, angularity: dict, dimorphism: dict, health: dict) -> dict:
        """Compute pillar scores and overall score."""

        # Pillar averages
        harmony_avg = self._pillar_average(harmony)
        angularity_avg = self._pillar_average(angularity)
        dimorphism_avg = self._pillar_average(dimorphism)
        health_avg = self._health_average(health)

        # Overall score (weighted)
        overall = (
            harmony_avg * self.PILLAR_WEIGHTS["harmony"]
            + angularity_avg * self.PILLAR_WEIGHTS["angularity"]
            + dimorphism_avg * self.PILLAR_WEIGHTS["dimorphism"]
            + health_avg * self.PILLAR_WEIGHTS["health"]
        )

        # Identify strengths and weaknesses
        all_metrics = self._flatten_metrics(harmony, angularity, dimorphism, health)
        strengths = sorted(all_metrics, key=lambda x: x["score"], reverse=True)[:5]
        weaknesses = sorted(all_metrics, key=lambda x: x["score"])[:5]

        # Generate improvement suggestions
        suggestions = self._generate_suggestions(all_metrics)

        return {
            "overall": {
                "score": round(overall, 1),
                "grade": self._score_to_grade(overall),
                "percentile": self._score_to_percentile(overall),
            },
            "pillars": {
                "harmony": {
                    "score": round(harmony_avg, 1),
                    "weight": self.PILLAR_WEIGHTS["harmony"],
                    "grade": self._score_to_grade(harmony_avg),
                    "description": "Facial proportional balance",
                },
                "angularity": {
                    "score": round(angularity_avg, 1),
                    "weight": self.PILLAR_WEIGHTS["angularity"],
                    "grade": self._score_to_grade(angularity_avg),
                    "description": "Jawline & bone structure definition",
                },
                "dimorphism": {
                    "score": round(dimorphism_avg, 1),
                    "weight": self.PILLAR_WEIGHTS["dimorphism"],
                    "grade": self._score_to_grade(dimorphism_avg),
                    "description": "Gender-specific trait balance",
                },
                "health": {
                    "score": round(health_avg, 1),
                    "weight": self.PILLAR_WEIGHTS["health"],
                    "grade": self._score_to_grade(health_avg),
                    "description": "Skin, symmetry & feature health",
                },
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
        }

    def _pillar_average(self, pillar_data: dict) -> float:
        """Average all scores in a pillar."""
        scores = []
        for key, value in pillar_data.items():
            if isinstance(value, dict) and "score" in value:
                scores.append(value["score"])
        return np.mean(scores) if scores else 5.0

    def _health_average(self, health_data: dict) -> float:
        """Average scores across all health sub-categories."""
        scores = []
        for category in health_data.values():
            if isinstance(category, dict):
                for key, value in category.items():
                    if isinstance(value, dict) and "score" in value:
                        scores.append(value["score"])
        return np.mean(scores) if scores else 5.0

    def _flatten_metrics(self, harmony, angularity, dimorphism, health) -> list:
        """Flatten all metrics into a single list with category labels."""
        metrics = []

        for name, data in harmony.items():
            if isinstance(data, dict) and "score" in data:
                metrics.append({
                    "name": name,
                    "score": data["score"],
                    "category": "Harmony",
                    "description": data.get("description", ""),
                })

        for name, data in angularity.items():
            if isinstance(data, dict) and "score" in data:
                metrics.append({
                    "name": name,
                    "score": data["score"],
                    "category": "Angularity",
                    "description": data.get("description", ""),
                })

        for name, data in dimorphism.items():
            if isinstance(data, dict) and "score" in data:
                metrics.append({
                    "name": name,
                    "score": data["score"],
                    "category": "Dimorphism",
                    "description": data.get("description", ""),
                })

        for cat_name, cat_data in health.items():
            if isinstance(cat_data, dict):
                for name, data in cat_data.items():
                    if isinstance(data, dict) and "score" in data:
                        metrics.append({
                            "name": f"{cat_name}.{name}" if cat_name != "overall_health" else name,
                            "score": data["score"],
                            "category": "Health",
                            "description": data.get("description", ""),
                        })

        return metrics

    def _generate_suggestions(self, metrics: list) -> list:
        """Generate improvement suggestions based on weakest metrics."""
        suggestions = []
        weak = [m for m in metrics if m["score"] < 6.0]
        weak.sort(key=lambda x: x["score"])

        suggestion_map = {
            "harmony.facial_thirds": "Focus on mewing and proper tongue posture to improve facial proportions over time.",
            "harmony.facial_fifths": "Eye spacing is largely genetic, but facial exercises can improve overall harmony.",
            "harmony.golden_ratio": "Work on overall facial balance through targeted exercises and grooming.",
            "harmony.lower_face_third": "Lip and chin exercises can help balance the lower face third.",
            "harmony.eye_mouth_proportion": "Facial exercises targeting midface width can improve this ratio.",

            "angularity.gonial_angle": "Chewing hard gum (mastic gum) 20 min/day can sharpen jaw angle over months.",
            "angularity.jawline_definition": "Jawline exercises, body fat reduction, and proper tongue posture (mewing) improve definition.",
            "angularity.chin_projection": "Chin exercises and proper oral posture can improve projection over time.",
            "angularity.bizygomatic_width": "Cheekbone prominence is mostly genetic — contouring makeup can create visual effect.",
            "angularity.facial_wh_ratio": "Reducing body fat percentage can improve facial width-to-height ratio.",
            "angularity.mandible_length": "Jaw exercises may help — significant changes require orthodontic/surgical intervention.",
            "angularity.ramus_height": "Proper oral posture and jaw exercises can support ramus development.",
            "angularity.bigonial_width": "Chewing exercises can modestly increase bigonial width over time.",

            "dimorphism.brow_ridge": "Brow ridge prominence is largely genetic and develops during puberty.",
            "dimorphism.jaw_squareness": "Jaw exercises and chewing hard foods can increase jaw squareness.",
            "dimorphism.lip_fullness": "Hydration, lip care, and avoiding sun damage maintain lip fullness.",
            "dimorphism.brow_position": "Eyebrow grooming and shaping can optimize brow position visually.",

            "health.skin.uniformity": "Consistent skincare routine: cleanse, moisturize, SPF 30+ daily.",
            "health.skin.smoothness": "Exfoliation 2-3x/week, retinol for texture, and adequate hydration.",
            "health.eye_area.canthal_tilt": "Eye area is mostly genetic — sleep and hydration help the area look its best.",
            "health.eye_area.under_eye": "Adequate sleep, hydration, and vitamin C serum can improve under-eye appearance.",
            "health.nose.nose_width_ratio": "Non-surgical rhinoplasty (fillers) can refine nose width if desired.",
            "health.brows.brow_arch": "Professional eyebrow shaping can optimize arch and frame the face.",
            "health.proportions.facial_convexity": "Facial exercises and proper posture can support profile alignment.",
            "health.age_indicators.midface_volume": "Facial exercises targeting cheeks can maintain midface volume.",
        }

        for m in weak:
            suggestion = suggestion_map.get(m["name"], f"Focus on improving {m['name']} (currently {m['score']}/10).")
            suggestions.append({
                "metric": m["name"],
                "current_score": m["score"],
                "category": m["category"],
                "suggestion": suggestion,
                "priority": "high" if m["score"] < 4.0 else "medium",
            })

        return suggestions

    def _score_to_grade(self, score: float) -> str:
        if score >= 9.0:
            return "Exceptional"
        elif score >= 8.0:
            return "Excellent"
        elif score >= 7.0:
            return "Very Good"
        elif score >= 6.0:
            return "Good"
        elif score >= 5.0:
            return "Average"
        elif score >= 4.0:
            return "Below Average"
        elif score >= 3.0:
            return "Needs Improvement"
        else:
            return "Significant Improvement Needed"

    def _score_to_percentile(self, score: float) -> int:
        """Rough percentile estimate based on score distribution."""
        # Approximate normal distribution centered at 5.5, std dev ~1.5
        from scipy import stats
        try:
            percentile = int(stats.norm.cdf(score, loc=5.5, scale=1.5) * 100)
            return max(1, min(99, percentile))
        except ImportError:
            # Fallback without scipy
            mapping = {
                3.0: 5, 3.5: 10, 4.0: 16, 4.5: 25,
                5.0: 35, 5.5: 50, 6.0: 65, 6.5: 75,
                7.0: 84, 7.5: 90, 8.0: 95, 8.5: 97,
                9.0: 99, 9.5: 99,
            }
            for s in sorted(mapping.keys()):
                if score <= s:
                    return mapping[s]
            return 99

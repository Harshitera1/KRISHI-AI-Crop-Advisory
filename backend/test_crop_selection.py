import unittest
from unittest.mock import patch

from flask import Flask

from controllers.crop_controller import _crop_key, _suitable_crops, get_crop


class CropSelectionRegressionTests(unittest.TestCase):
    def test_crop_keys_match_case_and_spacing_without_aliases(self):
        self.assertEqual(_crop_key("Kidney Beans"), _crop_key("kidneybeans"))
        self.assertNotEqual(_crop_key("Groundnut"), _crop_key("Chickpea"))

    def test_profile_crops_are_authoritative_when_partially_supported(self):
        profile = {"crops": ["Sugarcane", "Arecanut", "Coconut", "Maize"]}
        self.assertEqual(
            _suitable_crops(profile, ["Rice"]),
            ["Sugarcane", "Arecanut", "Coconut", "Maize"],
        )

    def test_empty_profile_does_not_fall_back_to_location_crops(self):
        self.assertEqual(_suitable_crops({"crops": []}, ["Rice"]), [])

    @patch("controllers.crop_controller.cards_for", return_value=[])
    @patch("controllers.crop_controller.recommend_fertilizer")
    @patch("controllers.crop_controller.history_collection", None)
    @patch("controllers.crop_controller.predict_crop")
    @patch("controllers.crop_controller.get_weather_by_coords")
    @patch("controllers.crop_controller._stored_soil_profile")
    @patch("controllers.crop_controller.find_nearest_location")
    @patch("controllers.crop_controller._resolve_coordinates")
    def test_bengaluru_drops_zero_probability_and_keeps_profile_matches(
        self,
        resolve,
        nearest,
        stored,
        weather,
        predict,
        fertilizer,
        _cards,
    ):
        resolve.return_value = {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "name": "Bengaluru",
            "state": "Karnataka",
        }
        nearest.return_value = {
            "location": "Bengaluru",
            "region": "South",
            "state": "Karnataka",
            "crops": ["Rice"],
            "proximity_level": "local",
        }
        stored.return_value = {
            "N": 32,
            "P": 15,
            "K": 140,
            "ph": 6.5,
            "crops": ["Sugarcane", "Arecanut", "Coconut", "Maize"],
        }
        weather.return_value = {
            "success": True,
            "temperature": 27,
            "humidity": 74,
            "seasonal_rainfall_mm": 780,
        }
        predict.return_value = [
            {"crop": "coconut", "confidence": 0.08},
            {"crop": "maize", "confidence": 0.0},
            {"crop": "rice", "confidence": 0.4},
        ]

        with Flask(__name__).app_context():
            result = get_crop(
                {
                    "location": "Bengaluru",
                    "soil": "Sandy",
                    "N": 32,
                    "P": 15,
                    "K": 140,
                    "ph": 6.5,
                }
            )

        self.assertEqual([item["crop"] for item in result["top_3"]], ["coconut"])
        self.assertEqual(result["top_3"][0]["fit"], "soil_profile")
        fertilizer.assert_called_once_with(
            "coconut",
            latitude=12.9716,
            longitude=77.5946,
            city="Bengaluru",
        )

    @patch("controllers.crop_controller.cards_for", return_value=[])
    @patch("controllers.crop_controller.recommend_fertilizer")
    @patch("controllers.crop_controller.history_collection", None)
    @patch("controllers.crop_controller.predict_crop")
    @patch("controllers.crop_controller.get_weather_by_coords")
    @patch("controllers.crop_controller._stored_soil_profile")
    @patch("controllers.crop_controller.find_nearest_location")
    @patch("controllers.crop_controller._resolve_coordinates")
    def test_jaipur_does_not_fall_back_to_unlisted_model_crops(
        self,
        resolve,
        nearest,
        stored,
        weather,
        predict,
        fertilizer,
        _cards,
    ):
        resolve.return_value = {
            "latitude": 26.9124,
            "longitude": 75.7873,
            "name": "Jaipur",
            "state": "Rajasthan",
        }
        nearest.return_value = {
            "location": "Jaipur",
            "region": "West",
            "state": "Rajasthan",
            "crops": ["Rice"],
            "proximity_level": "local",
        }
        stored.return_value = {
            "N": 20,
            "P": 10,
            "K": 100,
            "ph": 7.8,
            "crops": ["Bajra", "Jowar", "Groundnut", "Mustard"],
        }
        weather.return_value = {
            "success": True,
            "temperature": 42,
            "humidity": 18,
            "seasonal_rainfall_mm": 12,
        }
        predict.return_value = [
            {"crop": "pomegranate", "confidence": 0.4},
            {"crop": "chickpea", "confidence": 0.3},
            {"crop": "orange", "confidence": 0.2},
        ]

        with Flask(__name__).app_context():
            result = get_crop(
                {
                    "location": "Jaipur",
                    "soil": "Sandy",
                    "N": 20,
                    "P": 10,
                    "K": 100,
                    "ph": 7.8,
                }
            )

        self.assertTrue(result["success"])
        self.assertFalse(result["recommendation_available"])
        self.assertEqual(result["top_3"], [])
        self.assertIsNone(result["recommended_crop"])
        self.assertIsNone(result["fertilizer"])
        fertilizer.assert_not_called()


if __name__ == "__main__":
    unittest.main()

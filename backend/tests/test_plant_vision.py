
from simulation.biology import __init__  # Ensure package is available
from app.services.plant_vision import interpret_predictions


def test_crop_identification():
    result = interpret_predictions([
        {"label": "Tomato___healthy", "score": 0.60},
        {"label": "Tomato___Early_Blight", "score": 0.25},
        {"label": "Corn_(maize)___Northern_Leaf_Blight", "score": 0.15},
    ])

    assert result["crop_identification"]["crop"] == "Tomato"
    assert result["diagnosis"]["status"] == "healthy_prediction"


def test_disease_classification():
    result = interpret_predictions([
        {
            "label": "Corn_(maize)___Northern_Leaf_Blight",
            "score": 0.80,
        },
        {
            "label": "Corn_(maize)___Common_Rust",
            "score": 0.10,
        },
        {
            "label": "Tomato___healthy",
            "score": 0.10,
        },
    ])

    assert result["crop_identification"]["crop"] == "Corn (maize)"
    assert result["diagnosis"]["status"] == "possible_disease"
    assert result["diagnosis"]["predicted_condition"] == "Northern Leaf Blight"
    assert result["condition_information"]["category"] == "Fungal disease"


def test_uncertain_prediction():
    result = interpret_predictions([
        {"label": "Tomato___Early_Blight", "score": 0.20},
        {"label": "Corn_(maize)___Common_Rust", "score": 0.18},
        {"label": "Apple___healthy", "score": 0.15},
    ])

    assert result["status"] == "uncertain"
    assert result["diagnosis"]["status"] == "uncertain"
    assert result["diagnosis"]["predicted_condition"] is None


def test_guidance_is_not_claimed_as_visual_detection():
    result = interpret_predictions([
        {
            "label": "Corn_(maize)___Northern_Leaf_Blight",
            "score": 0.90,
        },
        {
            "label": "Tomato___healthy",
            "score": 0.10,
        },
    ])

    limitations = result["limitations"]

    assert any(
        "not verified visual findings" in item
        for item in limitations
    )


if __name__ == "__main__":
    test_crop_identification()
    test_disease_classification()
    test_uncertain_prediction()
    test_guidance_is_not_claimed_as_visual_detection()

    print("All plant vision tests passed!")

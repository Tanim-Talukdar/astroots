
from collections import defaultdict
from io import BytesIO
import re

from PIL import (
    Image,
    ImageOps,
    UnidentifiedImageError,
)

MODEL_ID = "neghani/plantvillage-mobilenetv2"

MAX_IMAGE_SIZE = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MIN_IMAGE_DIMENSION = 64

# These are conservative prototype thresholds, not clinically
# or scientifically calibrated confidence levels.
MIN_CROP_CONFIDENCE = 0.50
MIN_CLASS_CONFIDENCE = 0.35
MIN_CONDITIONAL_CONFIDENCE = 0.55

_classifier = None


DISEASE_GUIDANCE = {
    "Northern Leaf Blight": {
        "category": "Fungal disease",
        "typical_symptoms": [
            "Long, cigar-shaped gray-green or brown leaf lesions",
            "Lesions may enlarge and merge",
            "Severely affected leaves may dry out",
        ],
        "possible_causes": [
            "Infection by a plant-pathogenic fungus",
            "Extended leaf wetness and favorable humidity",
            "Infected crop residue",
        ],
        "recommended_actions": [
            "Inspect nearby leaves for similar lesions",
            "Remove heavily affected plant debris where practical",
            "Improve airflow and avoid prolonged leaf wetness",
            "Confirm the diagnosis with a local agricultural expert",
        ],
    },
    "Early Blight": {
        "category": "Fungal disease",
        "typical_symptoms": [
            "Brown lesions, often with concentric rings",
            "Yellowing around affected leaf areas",
            "Older leaves may be affected first",
        ],
        "possible_causes": [
            "Fungal infection",
            "Wet foliage and high humidity",
            "Infected plant debris",
        ],
        "recommended_actions": [
            "Inspect lower and older leaves",
            "Remove badly affected leaves when appropriate",
            "Avoid overhead watering",
            "Keep foliage dry and improve airflow",
        ],
    },
    "Late Blight": {
        "category": "Oomycete disease",
        "typical_symptoms": [
            "Irregular water-soaked-looking lesions",
            "Brown or dark areas on leaves",
            "White growth may appear under humid conditions",
        ],
        "possible_causes": [
            "Infection by Phytophthora infestans",
            "Cool, humid weather and prolonged leaf wetness",
        ],
        "recommended_actions": [
            "Isolate suspicious plants when possible",
            "Inspect neighboring plants immediately",
            "Avoid moving wet plant material between zones",
            "Seek prompt expert confirmation",
        ],
    },
    "Bacterial Spot": {
        "category": "Bacterial disease",
        "typical_symptoms": [
            "Small dark brown or black spots",
            "Spots may have yellow halos",
            "Affected tissue may become dry or irregular",
        ],
        "possible_causes": [
            "Bacterial infection",
            "Splashing water and contaminated plant material",
        ],
        "recommended_actions": [
            "Avoid handling plants while foliage is wet",
            "Remove heavily affected debris carefully",
            "Sanitize tools between plants",
            "Seek expert confirmation before treatment",
        ],
    },
    "Powdery Mildew": {
        "category": "Fungal disease",
        "typical_symptoms": [
            "White powder-like patches on leaf surfaces",
            "Leaf yellowing or distortion",
            "Reduced leaf vigor in severe cases",
        ],
        "possible_causes": [
            "Powdery mildew fungal infection",
            "Poor airflow and favorable humidity conditions",
        ],
        "recommended_actions": [
            "Improve airflow around plants",
            "Inspect both sides of affected leaves",
            "Remove severely affected debris",
            "Monitor nearby plants for spreading symptoms",
        ],
    },
    "Leaf Mold": {
        "category": "Fungal disease",
        "typical_symptoms": [
            "Yellowish patches on upper leaf surfaces",
            "Olive-green or gray growth underneath leaves",
            "Leaf deterioration in severe cases",
        ],
        "possible_causes": [
            "Fungal infection",
            "High greenhouse humidity and poor airflow",
        ],
        "recommended_actions": [
            "Improve greenhouse ventilation",
            "Monitor humidity",
            "Avoid prolonged leaf wetness",
            "Inspect neighboring plants",
        ],
    },
}


def _clean_label(value: str) -> str:
    value = value.replace("_", " ").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def _parse_prediction(item: dict) -> tuple[str, str, float]:
    label = str(item.get("label", ""))
    score = float(item.get("score", 0.0))

    if not label:
        raise ValueError("The model returned an invalid label.")

    if not 0.0 <= score <= 1.0:
        raise ValueError("The model returned an invalid confidence score.")

    if "___" not in label:
        return "Unknown", label, score

    crop_label, condition_label = label.split("___", 1)

    return (
        _clean_label(crop_label),
        _clean_label(condition_label),
        score,
    )


def _get_guidance(condition: str) -> dict:
    if condition.lower() == "healthy":
        return {
            "category": "No disease detected by this classifier",
            "typical_symptoms": [],
            "possible_causes": [],
            "recommended_actions": [
                "Continue regular plant monitoring",
                "Maintain suitable irrigation and nutrition",
                "Inspect leaves regularly for new changes",
            ],
        }

    for disease_name, guidance in DISEASE_GUIDANCE.items():
        if disease_name.lower() in condition.lower():
            return guidance

    return {
        "category": "Unclassified plant condition",
        "typical_symptoms": [
            "The model assigned this disease or condition label.",
            "Its characteristic symptoms have not been independently verified.",
        ],
        "possible_causes": [
            "The cause cannot be confirmed from this prediction alone."
        ],
        "recommended_actions": [
            "Inspect the affected plant closely",
            "Compare symptoms with a trusted agricultural reference",
            "Monitor nearby plants",
            "Seek expert confirmation before applying treatment",
        ],
    }


def interpret_predictions(predictions: list[dict]) -> dict:
    if not predictions:
        raise ValueError("The model returned no predictions.")

    crop_scores = defaultdict(float)
    parsed = []

    for item in predictions:
        crop, condition, score = _parse_prediction(item)

        parsed.append({
            "crop": crop,
            "condition": condition,
            "score": score,
            "label": str(item["label"]),
        })

        crop_scores[crop] += score

    if not parsed:
        raise ValueError("No usable predictions were returned.")

    best_crop = max(crop_scores, key=crop_scores.get)
    crop_confidence = min(crop_scores[best_crop], 1.0)

    crop_predictions = sorted(
        [
            {
                "crop": crop,
                "confidence": round(min(score, 1.0), 4),
            }
            for crop, score in crop_scores.items()
        ],
        key=lambda item: item["confidence"],
        reverse=True,
    )

    # Select the strongest condition within the most likely crop.
    crop_classes = [
        item for item in parsed
        if item["crop"] == best_crop
    ]

    best_condition = max(
        crop_classes,
        key=lambda item: item["score"],
    )

    raw_confidence = best_condition["score"]

    conditional_confidence = (
        raw_confidence / crop_confidence
        if crop_confidence > 0
        else 0.0
    )

    condition = best_condition["condition"]
    is_healthy = condition.lower() == "healthy"

    reliable_enough = (
        crop_confidence >= MIN_CROP_CONFIDENCE
        and raw_confidence >= MIN_CLASS_CONFIDENCE
        and conditional_confidence >= MIN_CONDITIONAL_CONFIDENCE
    )

    if not reliable_enough:
        status = "uncertain"
        diagnosis_status = "uncertain"
        predicted_condition = None
        guidance = {
            "category": "Uncertain prediction",
            "typical_symptoms": [],
            "possible_causes": [],
            "recommended_actions": [
                "Upload a clearer close-up image",
                "Capture the affected leaf in natural lighting",
                "Seek expert confirmation if symptoms persist",
            ],
        }
    elif is_healthy:
        status = "prediction_available"
        diagnosis_status = "healthy_prediction"
        predicted_condition = "Healthy"
        guidance = _get_guidance("Healthy")
    else:
        status = "prediction_available"
        diagnosis_status = "possible_disease"
        predicted_condition = condition
        guidance = _get_guidance(condition)

    return {
        "status": status,
        "prediction_type": "AI image classification",
        "crop_identification": {
            "crop": best_crop,
            "confidence": round(crop_confidence, 4),
            "confidence_type": "aggregated class probability",
            "candidates": crop_predictions[:5],
        },
        "diagnosis": {
            "status": diagnosis_status,
            "predicted_condition": predicted_condition,
            "raw_class_confidence": round(raw_confidence, 4),
            "conditional_confidence": round(
                conditional_confidence, 4
            ),
            "confidence_is_calibrated": False,
        },
        "condition_information": guidance,
        "top_predictions": [
            {
                "label": item["label"],
                "crop": item["crop"],
                "condition": item["condition"],
                "confidence": round(item["score"], 4),
            }
            for item in sorted(
                parsed,
                key=lambda item: item["score"],
                reverse=True,
            )[:5]
        ],
        "model": MODEL_ID,
        "limitations": [
            "This model uses PlantVillage image classes.",
            "Crop identification is inferred from disease-class labels.",
            "Crop and disease predictions are not independently verified.",
            "Confidence scores are not calibrated probabilities of correctness.",
            "Typical symptoms are reference information, not verified visual findings.",
            "Real-world images may produce incorrect predictions.",
            "This output is not a confirmed agricultural diagnosis.",
        ],
    }


def analyze_plant_image(image_bytes: bytes) -> dict:
    global _classifier

    if not image_bytes or len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError("Image must be between 1 byte and 8 MB.")

    try:
        with Image.open(BytesIO(image_bytes)) as source:
            source.verify()

        with Image.open(BytesIO(image_bytes)) as source:
            if source.width < MIN_IMAGE_DIMENSION:
                raise ValueError("Image width is too small.")

            if source.height < MIN_IMAGE_DIMENSION:
                raise ValueError("Image height is too small.")

            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image dimensions are too large.")

            image = ImageOps.exif_transpose(source).convert("RGB")

    except ValueError:
        raise
    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
    ) as error:
        raise ValueError(
            "Invalid, unsupported, or unsafe image file."
        ) from error

    if _classifier is None:
        from transformers import pipeline

        _classifier = pipeline(
            "image-classification",
            model=MODEL_ID,
            device=-1,
        )

    # PlantVillage MobileNetV2 has 38 disease/healthy classes.
    predictions = _classifier(image, top_k=38)

    return interpret_predictions(predictions)

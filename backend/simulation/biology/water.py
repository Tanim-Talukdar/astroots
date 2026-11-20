
def calculate_water_stress(
    soil_moisture: float,
    wilting_point: float,
    field_capacity: float,
) -> float:
    """
    Relative soil-water availability factor between 0 and 1.

    Inputs must use the same moisture units.
    """
    if field_capacity <= wilting_point:
        raise ValueError(
            "Field capacity must exceed wilting point."
        )

    if soil_moisture <= wilting_point:
        return 0.0

    if soil_moisture >= field_capacity:
        return 1.0

    return (
        soil_moisture - wilting_point
    ) / (
        field_capacity - wilting_point
    )


def update_soil_moisture(
    current_moisture: float,
    irrigation_mm: float,
    evapotranspiration_mm: float,
    rainfall_mm: float = 0.0,
) -> float:
    """
    Simplified daily soil-water balance.

    Assumes a single soil layer and no runoff or drainage.
    """
    if min(
        current_moisture,
        irrigation_mm,
        evapotranspiration_mm,
        rainfall_mm,
    ) < 0:
        raise ValueError("Water inputs cannot be negative.")

    return max(
        0.0,
        current_moisture
        + irrigation_mm
        + rainfall_mm
        - evapotranspiration_mm,
    )

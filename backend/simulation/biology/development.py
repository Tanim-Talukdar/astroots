
def calculate_thermal_time(
    temperature_c: float,
    base_temperature_c: float,
    maximum_temperature_c: float,
) -> float:
    """
    Simplified growing degree-day calculation.
    Temperatures above the maximum are capped.
    """
    effective_temperature = min(
        temperature_c,
        maximum_temperature_c
    )

    return max(
        0.0,
        effective_temperature - base_temperature_c
    )


def calculate_temperature_stress(
    temperature_c: float,
    base_temperature_c: float,
    optimal_temperature_c: float,
    maximum_temperature_c: float,
) -> float:
    """
    Returns a temperature suitability factor between 0 and 1.
    This is a simplified response, not a validated crop response curve.
    """
    if temperature_c <= base_temperature_c:
        return 0.0

    if temperature_c <= optimal_temperature_c:
        return (
            temperature_c - base_temperature_c
        ) / (
            optimal_temperature_c - base_temperature_c
        )

    if temperature_c <= maximum_temperature_c:
        return (
            maximum_temperature_c - temperature_c
        ) / (
            maximum_temperature_c - optimal_temperature_c
        )

    return 0.0

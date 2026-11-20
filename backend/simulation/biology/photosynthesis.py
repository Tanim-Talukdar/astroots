
def calculate_light_interception(
    canopy_cover_percent: float,
) -> float:
    """
    Estimates the fraction of light intercepted by the canopy.
    """
    if not 0 <= canopy_cover_percent <= 100:
        raise ValueError(
            "Canopy cover must be between 0 and 100."
        )

    return canopy_cover_percent / 100.0


def calculate_biomass_gain(
    intercepted_par_mj: float,
    water_productivity: float,
    water_stress: float,
    temperature_stress: float,
) -> float:
    """
    Simplified water-productivity biomass estimate.

    intercepted_par_mj must be expressed as intercepted
    equivalent water-productivity input in the model's
    calibrated units before using this equation.

    This is a placeholder interface, not yet a calibrated
    photosynthesis model.
    """
    if intercepted_par_mj < 0 or water_productivity < 0:
        raise ValueError("Inputs cannot be negative.")

    if not 0 <= water_stress <= 1:
        raise ValueError("Water stress must be between 0 and 1.")

    if not 0 <= temperature_stress <= 1:
        raise ValueError(
            "Temperature stress must be between 0 and 1."
        )

    return (
        intercepted_par_mj
        * water_productivity
        * water_stress
        * temperature_stress
    )

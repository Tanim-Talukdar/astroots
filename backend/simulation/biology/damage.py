
from dataclasses import dataclass


@dataclass
class DamageResult:
    daily_tissue_loss_percent: float
    permanent_tissue_loss_percent: float
    living_tissue_factor: float
    biomass_after_damage_g: float
    canopy_after_damage_percent: float
    biomass_loss_g: float


def calculate_tissue_damage(
    health_score: float,
    previous_tissue_loss_percent: float,
    biomass_g: float,
    canopy_cover_percent: float,
) -> DamageResult:

    health = max(0.0, min(100.0, health_score))
    previous_loss = max(
        0.0,
        min(100.0, previous_tissue_loss_percent),
    )

    # Physical injury occurs under severe health stress.
    # Maximum assumed injury is 0.5% of existing tissue per day.
    daily_loss_fraction = max(
        0.0,
        (50.0 - health) / 50.0,
    ) * 0.005

    daily_loss_percent = daily_loss_fraction * 100

    # Permanent cumulative tissue loss.
    new_loss = 100 * (
        1 - (1 - previous_loss / 100)
        * (1 - daily_loss_fraction)
    )

    biomass_after = biomass_g * (1 - daily_loss_fraction)
    canopy_after = canopy_cover_percent * (
        1 - daily_loss_fraction
    )

    return DamageResult(
        daily_tissue_loss_percent=round(daily_loss_percent, 4),
        permanent_tissue_loss_percent=round(new_loss, 4),
        living_tissue_factor=round(1 - new_loss / 100, 4),
        biomass_after_damage_g=round(biomass_after, 6),
        canopy_after_damage_percent=round(canopy_after, 4),
        biomass_loss_g=round(
            biomass_g - biomass_after, 6
        ),
    )

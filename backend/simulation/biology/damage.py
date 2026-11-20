
from dataclasses import dataclass
import math


@dataclass
class DamageResult:
    daily_tissue_loss_percent: float
    permanent_tissue_loss_percent: float
    living_tissue_factor: float
    biomass_after_damage_g: float
    canopy_after_damage_percent: float
    biomass_loss_g: float


def _safe_number(value: float, default: float = 0.0) -> float:
    """Convert a value to a finite number."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    return number if math.isfinite(number) else default


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def calculate_tissue_damage(
    health_score: float,
    previous_tissue_loss_percent: float,
    biomass_g: float,
    canopy_cover_percent: float,
    damage_sensitivity: float = 1.0,
) -> DamageResult:
    """
    Estimate aggregate permanent tissue damage.

    Damage is applied when health falls below 50.

    Permanent tissue loss is cumulative and cannot recover.
    Recovery of reversible physiological stress is handled
    separately by recovery.py.

    damage_sensitivity is a provisional species-specific
    coefficient. A higher value increases estimated damage.

    This is a simplified prototype model, not a validated
    species-specific tissue injury model.
    """

    health = _clamp(
        _safe_number(health_score),
        0.0,
        100.0,
    )

    previous_loss = _clamp(
        _safe_number(previous_tissue_loss_percent),
        0.0,
        100.0,
    )

    biomass = max(0.0, _safe_number(biomass_g))

    canopy = _clamp(
        _safe_number(canopy_cover_percent),
        0.0,
        100.0,
    )

    sensitivity = _clamp(
        _safe_number(damage_sensitivity, 1.0),
        0.5,
        2.0,
    )

    # Maximum base daily tissue loss is 0.5%
    # at health score 0, before species sensitivity.
    daily_loss_fraction = (
        max(0.0, (50.0 - health) / 50.0)
        * 0.005
        * sensitivity
    )

    # Prevent excessive daily tissue loss.
    daily_loss_fraction = _clamp(
        daily_loss_fraction,
        0.0,
        0.01,
    )

    daily_loss_percent = daily_loss_fraction * 100.0

    # Combine today's damage with previous permanent tissue loss.
    permanent_loss = 100.0 * (
        1.0
        - (1.0 - previous_loss / 100.0)
        * (1.0 - daily_loss_fraction)
    )

    permanent_loss = _clamp(
        permanent_loss,
        0.0,
        100.0,
    )

    living_tissue_factor = (
        1.0 - permanent_loss / 100.0
    )

    biomass_after_damage = biomass * (
        1.0 - daily_loss_fraction
    )

    canopy_after_damage = canopy * (
        1.0 - daily_loss_fraction
    )

    biomass_loss = biomass - biomass_after_damage

    return DamageResult(
        daily_tissue_loss_percent=round(
            daily_loss_percent, 4
        ),
        permanent_tissue_loss_percent=round(
            permanent_loss, 4
        ),
        living_tissue_factor=round(
            living_tissue_factor, 4
        ),
        biomass_after_damage_g=round(
            biomass_after_damage, 4
        ),
        canopy_after_damage_percent=round(
            canopy_after_damage, 4
        ),
        biomass_loss_g=round(
            biomass_loss, 4
        ),
    )

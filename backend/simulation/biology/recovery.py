
from dataclasses import dataclass


@dataclass
class RecoveryResult:
    stress_days: int
    accumulated_stress: float
    damage_percent: float
    recovery_days: int
    recovery_rate: float
    plant_condition: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def calculate_recovery(
    previous_stress_days: int,
    previous_accumulated_stress: float,
    previous_damage_percent: float,
    previous_recovery_days: int,
    health_score: float,
    recovery_rate: float = 3.0,
) -> RecoveryResult:
    """
    Estimate accumulated physiological stress and recovery.

    Health <= 80 indicates continued environmental stress.
    Health > 80 allows recovery to begin.

    Permanent physical tissue loss is tracked separately
    by damage.py.
    """

    health = _clamp(float(health_score), 0.0, 100.0)

    stress_days = max(0, int(previous_stress_days))
    accumulated_stress = _clamp(
        float(previous_accumulated_stress), 0.0, 100.0
    )
    damage_percent = _clamp(
        float(previous_damage_percent), 0.0, 100.0
    )
    recovery_days = max(0, int(previous_recovery_days))

    daily_stress = 100.0 - health

    has_stress_history = (
        stress_days > 0
        or accumulated_stress > 0
        or damage_percent > 0
    )

    if daily_stress >= 20.0:
        stress_days += 1
        recovery_days = 0

        accumulated_stress = _clamp(
            accumulated_stress + daily_stress * 0.15,
            0.0,
            100.0,
        )

        damage_percent = _clamp(
            damage_percent + daily_stress * 0.025,
            0.0,
            100.0,
        )

        plant_condition = (
            "Critical Damage"
            if damage_percent >= 70
            else "Severe Damage"
            if damage_percent >= 40
            else "Moderate Damage"
            if damage_percent >= 15
            else "Under Stress"
        )

    else:
        if has_stress_history:
            recovery_days += 1

            recovery_factor = _clamp(
                (health - 50.0) / 50.0,
                0.0,
                1.0,
            )

            daily_recovery = _clamp(
                float(recovery_rate),
                0.0,
                10.0,
            )

            accumulated_stress = max(
                0.0,
                accumulated_stress - daily_recovery * recovery_factor,
            )

            damage_percent = max(
                0.0,
                damage_percent - 0.5 * recovery_factor,
            )

        if damage_percent >= 70:
            plant_condition = "Critical Damage"
        elif damage_percent >= 40:
            plant_condition = "Severe Damage"
        elif damage_percent >= 15:
            plant_condition = "Moderate Damage"
        elif has_stress_history and (
            accumulated_stress > 0 or damage_percent > 0
        ):
            plant_condition = "Recovering"
        elif has_stress_history:
            plant_condition = "Recovered"
        else:
            plant_condition = "Healthy"

    return RecoveryResult(
        stress_days=stress_days,
        accumulated_stress=round(accumulated_stress, 4),
        damage_percent=round(damage_percent, 4),
        recovery_days=recovery_days,
        recovery_rate=round(100.0 - damage_percent, 2),
        plant_condition=plant_condition,
    )

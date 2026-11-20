
from dataclasses import dataclass


@dataclass
class RecoveryResult:
    stress_days: int
    accumulated_stress: float
    damage_percent: float
    recovery_days: int
    recovery_rate: float
    plant_condition: str


def calculate_recovery(
    previous_stress_days: int,
    previous_accumulated_stress: float,
    previous_damage_percent: float,
    previous_recovery_days: int,
    health_score: float,
) -> RecoveryResult:

    # Stress is measured as the deficit from a perfect health score.
    daily_stress = max(0.0, min(100.0, 100.0 - health_score))

    stress_days = previous_stress_days
    accumulated_stress = previous_accumulated_stress
    damage = previous_damage_percent
    recovery_days = previous_recovery_days

    if daily_stress >= 20:
        stress_days += 1
        recovery_days = 0

        # Repeated stress accumulates more damage over time.
        accumulated_stress = min(
            100.0,
            accumulated_stress + daily_stress * 0.15,
        )

        damage = min(
            100.0,
            damage + daily_stress * 0.025,
        )

    else:
        recovery_days += 1
        stress_days = max(0, stress_days - 1)

        # Recovery is gradual and cannot erase accumulated damage instantly.
        accumulated_stress = max(
            0.0,
            accumulated_stress - 3.0,
        )

        damage = max(
            0.0,
            damage - 0.5,
        )

    recovery_rate = max(
        0.0,
        min(100.0, 100.0 - damage),
    )

    if damage >= 70:
        condition = "Critical Damage"
    elif damage >= 40:
        condition = "Severe Damage"
    elif damage >= 15:
        condition = "Moderate Damage"
    elif daily_stress >= 20:
        condition = "Under Stress"
    elif damage > 0:
        condition = "Recovering"
    else:
        condition = "Healthy"

    return RecoveryResult(
        stress_days=stress_days,
        accumulated_stress=round(accumulated_stress, 2),
        damage_percent=round(damage, 2),
        recovery_days=recovery_days,
        recovery_rate=round(recovery_rate, 2),
        plant_condition=condition,
    )


from simulation.biology.lifecycle import calculate_lifecycle


def test_tomato_lifecycle():
    flowering = calculate_lifecycle("tomato", 750, 100)
    fruiting = calculate_lifecycle("tomato", 1100, 200)
    mature = calculate_lifecycle("tomato", 1400, 300)

    assert flowering.flowering_progress_percent > 0
    assert fruiting.fruit_development_percent > 0
    assert mature.harvest_readiness_percent == 100
    assert mature.harvest_status == "ready"


def test_cucumber_lifecycle():
    result = calculate_lifecycle("cucumber", 800, 100)

    assert result.fruit_development_percent > 0
    assert result.estimated_yield_g == 70


def test_lettuce_lifecycle():
    growing = calculate_lifecycle("lettuce", 300, 100)
    mature = calculate_lifecycle("lettuce", 600, 100)

    assert growing.harvest_readiness_percent == 50
    assert mature.harvest_readiness_percent == 100
    assert mature.harvest_status == "ready"


if __name__ == "__main__":
    test_tomato_lifecycle()
    test_cucumber_lifecycle()
    test_lettuce_lifecycle()
    print("All lifecycle tests passed!")

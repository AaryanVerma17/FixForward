from tools.safety_screen import screen_safety

def test_burning_smell_is_hazard():
    result = screen_safety({"symptoms": ["burning_smell"]})
    assert result["hazard"] is True

def test_ordinary_noise_not_hazard_by_rule():
    result = screen_safety({"symptoms": ["unusual_noise"]})
    assert result["hazard"] is False

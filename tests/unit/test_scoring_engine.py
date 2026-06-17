from app.agents.scoring_engine import ScoreComponents, ScoringEngine


def test_score_components_computes_total():
    comp = ScoreComponents(
        resume_match=80.0,
        hiring_probability=70.0,
        location_preference=90.0,
        freshness=85.0,
        company_quality=75.0,
        competition_estimate=60.0,
    )
    # 80 * 0.35 + 70 * 0.20 + 90 * 0.15 + 85 * 0.15 + 75 * 0.10 + 60 * 0.05
    # = 28 + 14 + 13.5 + 12.75 + 7.5 + 3 = 78.75
    assert abs(comp.total - 78.75) < 0.01


def test_score_band_classification():
    high_score = ScoreComponents(95.0, 100.0, 95.0, 100.0, 95.0, 100.0)
    assert high_score.band == "Dream Match"

    excellent = ScoreComponents(90.0, 90.0, 90.0, 90.0, 90.0, 90.0)
    assert excellent.band == "Excellent Match"

    strong = ScoreComponents(80.0, 80.0, 80.0, 80.0, 80.0, 80.0)
    assert strong.band == "Strong Match"

    good = ScoreComponents(70.0, 70.0, 70.0, 70.0, 70.0, 70.0)
    assert good.band == "Good Match"

    low = ScoreComponents(50.0, 50.0, 50.0, 50.0, 50.0, 50.0)
    assert low.band == "Low Priority"


def test_freshness_score_recent():
    score = ScoringEngine.freshness_score("2026-06-15", days_old_threshold=30)
    assert 90 < score <= 100


def test_freshness_score_old():
    score = ScoringEngine.freshness_score("2026-05-01", days_old_threshold=30)
    assert 0 <= score < 50


def test_location_score_preferred():
    score = ScoringEngine.location_score("Bengaluru, India")
    assert score == 100.0


def test_location_score_remote():
    score = ScoringEngine.location_score("Remote")
    assert score == 100.0


def test_location_score_non_preferred():
    score = ScoringEngine.location_score("London, UK")
    assert score == 50.0


def test_scoring_engine_compute():
    comp = ScoringEngine.default_components()
    total, band = ScoringEngine.compute(comp)
    assert 0 <= total <= 100
    assert band in ["Dream Match", "Excellent Match", "Strong Match", "Good Match", "Low Priority"]

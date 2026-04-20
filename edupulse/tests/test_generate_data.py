from backend.ml.generate_data import genereer_actieve_studenten, genereer_historische_studenten


def test_actieve_studenten_vorm():
    df = genereer_actieve_studenten(n=100)
    assert len(df) == 100
    assert "studentnummer" in df.columns
    assert "uitgevallen" not in df.columns


def test_historische_studenten_heeft_uitgevallen():
    df = genereer_historische_studenten(n=200)
    assert len(df) == 200
    assert "uitgevallen" in df.columns
    assert df["uitgevallen"].dtype == bool


def test_uitval_percentage_realistisch():
    df = genereer_historische_studenten(n=1000)
    pct = df["uitgevallen"].mean()
    assert 0.10 <= pct <= 0.35, f"Uitvalpercentage {pct:.1%} buiten verwacht bereik"


def test_aanwezigheid_range():
    df = genereer_actieve_studenten(n=200)
    assert df["aanwezigheid"].between(0.0, 1.0).all()


def test_cijfers_range():
    df = genereer_actieve_studenten(n=200)
    assert df["cijfer_nederlands"].between(1.0, 10.0).all()
    assert df["cijfer_rekenen"].between(1.0, 10.0).all()


def test_studentnummer_uniek():
    df = genereer_actieve_studenten(n=500)
    assert df["studentnummer"].is_unique

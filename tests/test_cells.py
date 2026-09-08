from wmbench.figures.cells import cell_rows
from wmbench.watermarkers import primaries


def thresholds():
    return {m: 3.0 for m in primaries}


def record(image, rung, score, domain):
    return {
        "image": image,
        "method": "trustmark_q",
        "condition": "jpeg_75",
        "family": "jpeg",
        "domain": domain,
        "rung": rung,
        "score": score,
        "bitacc": 1.0,
        "valid_fraction": 1.0,
        "corner_error": 0.1,
        "reg_method": "lightglue",
    }


def records():
    out = []
    for i, scores in enumerate([(5, 5, 5), (1, 5, 5), (1, 5, 1), (1, 1, 1)]):
        for rung, s in zip((1, 2, 3), scores):
            out.append(record(f"img{i}", rung, s, "photo" if i < 2 else "screen"))
    return out


def pooled_row(rows):
    return [r for r in rows if r["domain"] == "all"][0]


def test_rates_and_labels():
    rows = cell_rows(records(), thresholds(), thresholds(), True)
    row = pooled_row(rows)
    assert row["n"] == 4
    assert row["tpr_r1"] == 0.25
    assert row["tpr_r2"] == 0.75
    assert row["tpr_r3"] == 0.5
    assert row["label_survived"] == 0.25
    assert row["label_recoverable"] == 0.25
    assert row["label_sync_failed"] == 0.25
    assert row["label_destroyed"] == 0.25
    assert "tau_family_r1" not in row
    assert "recalibrated_rungs" not in row
    photo = [r for r in rows if r["domain"] == "photo"][0]
    assert photo["n"] == 2
    assert photo["tpr_r1"] == 0.5


def test_family_threshold_columns():
    family = {("trustmark_q", "jpeg", 1): 6.0}
    rows = cell_rows(records(), thresholds(), thresholds(), True, family_thresholds=family)
    row = pooled_row(rows)
    assert row["tpr_r1"] == 0.25
    assert row["tau_family_r1"] == 6.0
    assert row["tpr_family_r1"] == 0.0
    assert row["recalibrated_rungs"] == "1"
    assert "tau_family_r2" not in row
    assert row["label_survived"] == 0.25

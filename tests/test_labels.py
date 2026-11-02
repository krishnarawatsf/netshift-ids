import pytest

from netshift.labels import DROP, map_label


def test_benign():
    assert map_label("BENIGN") == "Benign"


def test_encoding_damaged_dash():
    assert map_label("Web Attack \ufffd Brute Force") == "Web attack"


def test_cse_style_names():
    assert map_label("DDoS attacks-LOIC-HTTP") == "DDoS"
    assert map_label("Brute Force -Web") == "Web attack"


def test_cse_2018_label_variants():
    assert map_label("DDOS attack-HOIC") == "DDoS"
    assert map_label("DDOS attack-LOIC-UDP") == "DDoS"
    assert map_label("DoS attacks-Synflooding") == "DoS"
    assert map_label("Infilteration") == DROP


def test_dropped_classes():
    assert map_label("PortScan") == DROP


def test_unknown_label_raises():
    with pytest.raises(KeyError):
        map_label("Something new")

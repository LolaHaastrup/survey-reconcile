from survey_reconcile.config import IdentifierConfig
from survey_reconcile.reconciliation.identifiers import normalise_identifier


def test_normalises_equivalent_household_identifiers():
    config = IdentifierConfig(remove_characters=("-", "/"))
    assert normalise_identifier(" osn-00 12 ", config) == "OSN0012"
    assert normalise_identifier("OSN/0012", config) == "OSN0012"


"""Tests for plugin.py."""
import pytest

from ckanext.summarystats.implementations import (
    is_eligible,
    calculate_stats,
)


@pytest.mark.ckan_config("ckan.plugins", "summarystats")
@pytest.mark.usefixtures("with_plugins")
def test_summarystats_by_itself(app):
    """
    Verify that summarystats get_eligibility_func() raises an error without an extension
    that implements the interface
    """
    dataset = None
    with pytest.raises(Exception) as excinfo:
        is_eligible(dataset)
    assert "No plugin implementing ISummaryStats was found." in str(excinfo.value)


@pytest.mark.ckan_config("ckan.plugins", "summarystats summarystats_mock_plugin")
@pytest.mark.usefixtures("with_plugins")
def test_mock_plugin_is_eligible(app):
    """
    Verify that summarystats get_eligibility_func() retrieves a custom is_eligible()
    method from a plugin that extends the ISummaryStats interface
    """
    dataset = None
    assert is_eligible(dataset) is True


@pytest.mark.ckan_config("ckan.plugins", "summarystats summarystats_mock_plugin")
@pytest.mark.usefixtures("with_plugins")
def test_mock_plugin_calculate_stats(app):
    """
    Verify that summarystats get_eligibility_func() retrieves a custom is_eligible()
    method from a plugin that extends the ISummaryStats interface
    """
    dataset = None
    result = calculate_stats(dataset)
    assert result[0][0] == "Dummy"

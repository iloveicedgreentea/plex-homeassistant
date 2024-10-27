"""Tests for the ezbeq sensors."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from syrupy import SnapshotAssertion

from homeassistant.const import STATE_UNKNOWN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import setup_integration

from pytest_homeassistant_custom_component.common import MockConfigEntry, snapshot_platform

pytestmark = pytest.mark.asyncio


async def test_sensor_setup_and_update(
    hass: HomeAssistant,
    mock_ezbeq_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test setup of sensor and data update."""
    with patch("custom_components.ezbeq.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    for device_name in mock_ezbeq_client.device_info:
        entity_id = f"sensor.{device_name.name}_current_profile"
        entry = entity_registry.async_get(entity_id)
        assert entry

        state = hass.states.get(entity_id)
        assert state
        assert state.state == "Test Profile"

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)

    # Simulate a data update
    mock_ezbeq_client.get_device_profile = MagicMock(return_value="New Test Profile")
    await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    for device_name in mock_ezbeq_client.device_info:
        entity_id = f"sensor.{device_name.name}_current_profile"
        state = hass.states.get(entity_id)
        assert state
        assert state.state == "New Test Profile"

    # Simulate a data update with unavailable data
    mock_ezbeq_client.get_device_profile = MagicMock(return_value=None)
    await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == STATE_UNKNOWN

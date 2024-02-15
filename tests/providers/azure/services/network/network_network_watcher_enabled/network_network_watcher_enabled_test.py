from unittest import mock
from uuid import uuid4

from azure.mgmt.network.models import NetworkWatcher

from prowler.providers.azure.services.network.network_service import SecurityGroup

AZURE_SUBSCRIPTION = str(uuid4())


class Test_network_network_watcher_enabled:
    def test_no_security_groups(self):
        network_client = mock.MagicMock
        network_client.security_groups = {}

        with mock.patch(
            "prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled.network_client",
            new=network_client,
        ):
            from prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled import (
                network_network_watcher_enabled,
            )

            check = network_network_watcher_enabled()
            result = check.execute()
            assert len(result) == 0

    def test_network_security_groups_no_network_watchers(self):
        network_client = mock.MagicMock
        security_group_name = "Security Group Name"
        security_group_id = str(uuid4())

        network_client.security_groups = {
            AZURE_SUBSCRIPTION: [
                SecurityGroup(
                    id=security_group_id,
                    name=security_group_name,
                    location="location",
                    security_rules=[],
                    network_watchers=[],
                    subscription_locations=["location"],
                    flow_logs=None,
                )
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled.network_client",
            new=network_client,
        ):
            from prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled import (
                network_network_watcher_enabled,
            )

            check = network_network_watcher_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Security Group {security_group_name} from subscription {AZURE_SUBSCRIPTION} has Network Watcher disabled for the following locations: {{'location'}}."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == security_group_name
            assert result[0].resource_id == security_group_id

    def test_network_security_groups_invalid_network_watchers_config(self):
        network_client = mock.MagicMock
        security_group_name = "Security Group Name"
        security_group_id = str(uuid4())

        network_client.security_groups = {
            AZURE_SUBSCRIPTION: [
                SecurityGroup(
                    id=security_group_id,
                    name=security_group_name,
                    location="location",
                    security_rules=None,
                    network_watchers=[NetworkWatcher(location="location2")],
                    subscription_locations=["location", "location2"],
                    flow_logs=None,
                )
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled.network_client",
            new=network_client,
        ):
            from prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled import (
                network_network_watcher_enabled,
            )

            check = network_network_watcher_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Security Group {security_group_name} from subscription {AZURE_SUBSCRIPTION} has Network Watcher disabled for the following locations: {{'location'}}."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == security_group_name
            assert result[0].resource_id == security_group_id

    def test_network_security_groups_valid_network_watchers_config(self):
        network_client = mock.MagicMock
        security_group_name = "Security Group Name"
        security_group_id = str(uuid4())

        network_client.security_groups = {
            AZURE_SUBSCRIPTION: [
                SecurityGroup(
                    id=security_group_id,
                    name=security_group_name,
                    location="location",
                    security_rules=None,
                    network_watchers=[NetworkWatcher(location="location")],
                    subscription_locations=["location"],
                    flow_logs=None,
                )
            ]
        }

        with mock.patch(
            "prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled.network_client",
            new=network_client,
        ):
            from prowler.providers.azure.services.network.network_network_watcher_enabled.network_network_watcher_enabled import (
                network_network_watcher_enabled,
            )

            check = network_network_watcher_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Security Group {security_group_name} from subscription {AZURE_SUBSCRIPTION} has Network Watcher enabled."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == security_group_name
            assert result[0].resource_id == security_group_id
from unittest import mock
from uuid import uuid4

from prowler.providers.azure.services.defender.defender_service import Defender_Settings

AZURE_SUSCRIPTION = str(uuid4())


class Test_defender_ensure_mcas_is_enabled:
    def test_defender_no_settings(self):
        defender_client = mock.MagicMock
        defender_client.settings = {}

        with mock.patch(
            "prowler.providers.azure.services.defender.defender_ensure_mcas_is_enabled.defender_ensure_mcas_is_enabled.defender_client",
            new=defender_client,
        ):
            from prowler.providers.azure.services.defender.defender_ensure_mcas_is_enabled.defender_ensure_mcas_is_enabled import (
                defender_ensure_mcas_is_enabled,
            )

            check = defender_ensure_mcas_is_enabled()
            result = check.execute()
            assert len(result) == 0

    def test_defender_mcas_disabled(self):
        resource_id = str(uuid4())
        defender_client = mock.MagicMock
        defender_client.settings = {
            AZURE_SUSCRIPTION: {
                "MCAS": Defender_Settings(
                    resource_id=resource_id,
                    resource_type="Microsoft.Security/locations/settings",
                    kind="DataExportSettings",
                    enabled=False,
                )
            }
        }

        with mock.patch(
            "prowler.providers.azure.services.defender.defender_ensure_mcas_is_enabled.defender_ensure_mcas_is_enabled.defender_client",
            new=defender_client,
        ):
            from prowler.providers.azure.services.defender.defender_ensure_mcas_is_enabled.defender_ensure_mcas_is_enabled import (
                defender_ensure_mcas_is_enabled,
            )

            check = defender_ensure_mcas_is_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Microsoft Defender for Cloud Apps is disabeld for subscription {AZURE_SUSCRIPTION}."
            )
            assert result[0].subscription == AZURE_SUSCRIPTION
            assert result[0].resource_name == "MCAS"
            assert result[0].resource_id == resource_id

    def test_defender_mcas_enabled(self):
        resource_id = str(uuid4())
        defender_client = mock.MagicMock
        defender_client.settings = {
            AZURE_SUSCRIPTION: {
                "MCAS": Defender_Settings(
                    resource_id=resource_id,
                    resource_type="Microsoft.Security/locations/settings",
                    kind="DataExportSettings",
                    enabled=True,
                )
            }
        }

        with mock.patch(
            "prowler.providers.azure.services.defender.defender_ensure_mcas_is_enabled.defender_ensure_mcas_is_enabled.defender_client",
            new=defender_client,
        ):
            from prowler.providers.azure.services.defender.defender_ensure_mcas_is_enabled.defender_ensure_mcas_is_enabled import (
                defender_ensure_mcas_is_enabled,
            )

            check = defender_ensure_mcas_is_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Microsoft Defender for Cloud Apps is enabled for susbscription {AZURE_SUSCRIPTION}."
            )
            assert result[0].subscription == AZURE_SUSCRIPTION
            assert result[0].resource_name == "MCAS"
            assert result[0].resource_id == resource_id
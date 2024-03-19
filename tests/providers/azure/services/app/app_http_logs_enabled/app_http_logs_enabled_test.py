from unittest import mock

from prowler.providers.azure.services.app.app_service import WebApp
from prowler.providers.azure.services.monitor.monitor_service import DiagnosticSetting
from tests.providers.azure.azure_fixtures import AZURE_SUBSCRIPTION


class Test_app_http_logs_enabled:

    def test_app_http_logs_enabled_no_subscriptions(self):
        app_client = mock.MagicMock
        app_client.apps = {}

        with mock.patch(
            "prowler.providers.azure.services.app.app_http_logs_enabled.app_http_logs_enabled.app_client",
            new=app_client,
        ):

            from prowler.providers.azure.services.app.app_http_logs_enabled.app_http_logs_enabled import (
                app_http_logs_enabled,
            )

            check = app_http_logs_enabled()
            result = check.execute()
            assert len(result) == 0

    def test_app_subscriptions_empty(self):
        app_client = mock.MagicMock
        app_client.apps = {AZURE_SUBSCRIPTION: {}}

        with mock.patch(
            "prowler.providers.azure.services.app.app_register_with_identity.app_register_with_identity.app_client",
            new=app_client,
        ):
            from prowler.providers.azure.services.app.app_register_with_identity.app_register_with_identity import (
                app_register_with_identity,
            )

            check = app_register_with_identity()
            result = check.execute()
            assert len(result) == 0

    def test_no_diagnostics_settings(self):
        app_client = mock.MagicMock()
        app_client.apps = {
            AZURE_SUBSCRIPTION: {
                "app1": WebApp(
                    resource_id="resource_id",
                    auth_enabled=True,
                    configurations=None,
                    client_cert_mode="Ignore",
                    https_only=False,
                    identity=None,
                )
            }
        }
        with mock.patch(
            "prowler.providers.azure.services.app.app_http_logs_enabled.app_http_logs_enabled.app_client",
            new=app_client,
        ):
            from prowler.providers.azure.services.app.app_http_logs_enabled.app_http_logs_enabled import (
                app_http_logs_enabled,
            )

            check = app_http_logs_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].resource_name == "app1"
            assert result[0].resource_id == "resource_id"
            assert (
                result[0].status_extended
                == f"Logging for app app1 HTTP Logs is disabled in subscription {AZURE_SUBSCRIPTION}."
            )
            assert result[0].subscription == AZURE_SUBSCRIPTION

    def test_diagnostic_setting_configured(self):
        app_client = mock.MagicMock
        app_client.apps = {
            AZURE_SUBSCRIPTION: {
                "app_id-1": WebApp(
                    resource_id="resource_id1",
                    auth_enabled=True,
                    configurations=None,
                    client_cert_mode="Ignore",
                    https_only=False,
                    identity=mock.MagicMock,
                    monitor_diagnostic_settings=[
                        DiagnosticSetting(
                            id="id1/id1",
                            logs=[
                                mock.MagicMock(
                                    category="AppServiceHTTPLogs",
                                    enabled=True,
                                ),
                                mock.MagicMock(
                                    category="AppServiceConsoleLogs",
                                    enabled=False,
                                ),
                                mock.MagicMock(
                                    category="AppServiceAppLogs",
                                    enabled=True,
                                ),
                                mock.MagicMock(
                                    category="AppServiceAuditLogs",
                                    enabled=False,
                                ),
                                mock.MagicMock(
                                    category="AppServiceIPSecAuditLogs",
                                    enabled=False,
                                ),
                                mock.MagicMock(
                                    category="AppServicePlatformLogs",
                                    enabled=False,
                                ),
                            ],
                            storage_account_name="storage_account_name1",
                            storage_account_id="storage_account_id1",
                            name="name_diagnostic_setting1",
                        ),
                    ],
                ),
                "app_id-2": WebApp(
                    resource_id="resource_id2",
                    auth_enabled=True,
                    configurations=None,
                    client_cert_mode="Ignore",
                    https_only=False,
                    identity=mock.MagicMock,
                    monitor_diagnostic_settings=[
                        DiagnosticSetting(
                            id="id2/id2",
                            logs=[
                                mock.MagicMock(
                                    category="AppServiceHTTPLogs",
                                    enabled=False,
                                ),
                                mock.MagicMock(
                                    category="AppServiceConsoleLogs",
                                    enabled=True,
                                ),
                                mock.MagicMock(
                                    category="AppServiceAppLogs",
                                    enabled=True,
                                ),
                                mock.MagicMock(
                                    category="AppServiceAuditLogs",
                                    enabled=False,
                                ),
                                mock.MagicMock(
                                    category="AppServiceIPSecAuditLogs",
                                    enabled=True,
                                ),
                                mock.MagicMock(
                                    category="AppServicePlatformLogs",
                                    enabled=False,
                                ),
                            ],
                            storage_account_name="storage_account_name2",
                            storage_account_id="storage_account_id2",
                            name="name_diagnostic_setting2",
                        ),
                    ],
                ),
            }
        }

        with mock.patch(
            "prowler.providers.azure.services.app.app_http_logs_enabled.app_http_logs_enabled.app_client",
            new=app_client,
        ):
            from prowler.providers.azure.services.app.app_http_logs_enabled.app_http_logs_enabled import (
                app_http_logs_enabled,
            )

            check = app_http_logs_enabled()
            result = check.execute()
            assert len(result) == 2
            assert result[0].status == "PASS"
            assert result[0].subscription == AZURE_SUBSCRIPTION
            assert result[0].resource_name == "name_diagnostic_setting1"
            assert result[0].resource_id == "id1/id1"
            assert (
                result[0].status_extended
                == f"Diagnostic setting name_diagnostic_setting1 has logging for app app_id-1 HTTP Logs enabled in subscription {AZURE_SUBSCRIPTION}"
            )
            assert result[1].status == "FAIL"
            assert result[1].subscription == AZURE_SUBSCRIPTION
            assert result[1].resource_name == "name_diagnostic_setting2"
            assert result[1].resource_id == "id2/id2"
            assert (
                result[1].status_extended
                == f"Diagnostic setting name_diagnostic_setting2 has not logging for app app_id-2 HTTP Logs enabled in subscription {AZURE_SUBSCRIPTION}"
            )
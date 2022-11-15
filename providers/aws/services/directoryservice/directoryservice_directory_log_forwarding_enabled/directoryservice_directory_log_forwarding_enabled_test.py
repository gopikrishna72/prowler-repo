from datetime import datetime
from unittest import mock

from providers.aws.services.directoryservice.directoryservice_service import (
    Directory,
    LogSubscriptions,
)

AWS_REGION = "eu-west-1"


class Test_directoryservice_directory_log_forwarding_enabled:
    def test_no_directories(self):
        directoryservice_client = mock.MagicMock
        directoryservice_client.directories = {}
        with mock.patch(
            "providers.aws.services.directoryservice.directoryservice_service.DirectoryService",
            new=directoryservice_client,
        ):
            # Test Check
            from providers.aws.services.directoryservice.directoryservice_directory_log_forwarding_enabled.directoryservice_directory_log_forwarding_enabled import (
                directoryservice_directory_log_forwarding_enabled,
            )

            check = directoryservice_directory_log_forwarding_enabled()
            result = check.execute()

            assert len(result) == 0

    def test_one_directory_logging_disabled(self):
        directoryservice_client = mock.MagicMock
        directory_name = "test-directory"
        directoryservice_client.directories = {
            directory_name: Directory(
                name=directory_name,
                region=AWS_REGION,
                log_subscriptions=[],
            )
        }
        with mock.patch(
            "providers.aws.services.directoryservice.directoryservice_service.DirectoryService",
            new=directoryservice_client,
        ):
            # Test Check
            from providers.aws.services.directoryservice.directoryservice_directory_log_forwarding_enabled.directoryservice_directory_log_forwarding_enabled import (
                directoryservice_directory_log_forwarding_enabled,
            )

            check = directoryservice_directory_log_forwarding_enabled()
            result = check.execute()

            assert len(result) == 1
            assert result[0].resource_id == "test-directory"
            assert result[0].region == AWS_REGION
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended
                == f"Directory Service {directory_name} have log forwarding to CloudWatch disabled"
            )

    def test_one_directory_logging_enabled(self):
        directoryservice_client = mock.MagicMock
        directory_name = "test-directory"
        directoryservice_client.directories = {
            directory_name: Directory(
                name=directory_name,
                region=AWS_REGION,
                log_subscriptions=[
                    LogSubscriptions(
                        log_group_name="test-log-group",
                        created_date_time=datetime(2022, 1, 1),
                    )
                ],
            )
        }
        with mock.patch(
            "providers.aws.services.directoryservice.directoryservice_service.DirectoryService",
            new=directoryservice_client,
        ):
            # Test Check
            from providers.aws.services.directoryservice.directoryservice_directory_log_forwarding_enabled.directoryservice_directory_log_forwarding_enabled import (
                directoryservice_directory_log_forwarding_enabled,
            )

            check = directoryservice_directory_log_forwarding_enabled()
            result = check.execute()

            assert len(result) == 1
            assert result[0].resource_id == "test-directory"
            assert result[0].region == AWS_REGION
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == f"Directory Service {directory_name} have log forwarding to CloudWatch enabled"
            )

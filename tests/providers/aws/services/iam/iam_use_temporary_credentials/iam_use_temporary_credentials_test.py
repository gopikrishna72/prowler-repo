from unittest import mock

from prowler.providers.aws.services.iam.iam_service import User

AWS_REGION = "us-east-1"
AWS_ACCOUNT_NUMBER = "123456789012"


class Test_iam_use_temporary_credentials:
    def test_no_access_keys(self):
        iam_client = mock.MagicMock
        iam_client.region = AWS_REGION
        iam_client.access_keys_metadata = [
            {"access_keys_metadata": [{"AccessKeyMetadata": []}]}
        ]
        iam_client.last_accessed_services = [
            {
                "user": User(
                    name="user1",
                    arn="user1-arn",
                    mfa_devices=[],
                    attached_policies=[],
                    inline_policies=[],
                ),
                "services": [{"ServiceNamespace": "ec2"}],
            }
        ]

        with mock.patch(
            "prowler.providers.aws.services.iam.iam_service.IAM", iam_client
        ):
            from prowler.providers.aws.services.iam.iam_use_temporary_credentials.iam_use_temporary_credentials import (
                iam_use_temporary_credentials,
            )

            check = iam_use_temporary_credentials()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"

    def test_access_keys_with_iam(self):
        iam_client = mock.MagicMock
        iam_client.region = AWS_REGION
        iam_client.access_keys_metadata = [
            {"access_keys_metadata": [{"AccessKeyMetadata": [{"AK1": 1}]}]}
        ]
        iam_client.last_accessed_services = [
            {
                "user": User(
                    name="user1",
                    arn="user1-arn",
                    mfa_devices=[],
                    attached_policies=[],
                    inline_policies=[],
                ),
                "services": [{"ServiceNamespace": "iam"}],
            }
        ]

        with mock.patch(
            "prowler.providers.aws.services.iam.iam_service.IAM", iam_client
        ):
            from prowler.providers.aws.services.iam.iam_use_temporary_credentials.iam_use_temporary_credentials import (
                iam_use_temporary_credentials,
            )

            check = iam_use_temporary_credentials()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"

    def test_access_keys_with_sts(self):
        iam_client = mock.MagicMock
        iam_client.region = AWS_REGION
        iam_client.access_keys_metadata = [
            {"access_keys_metadata": [{"AccessKeyMetadata": [{"AK1": 1}]}]}
        ]
        iam_client.last_accessed_services = [
            {
                "user": User(
                    name="user1",
                    arn="user1-arn",
                    mfa_devices=[],
                    attached_policies=[],
                    inline_policies=[],
                ),
                "services": [{"ServiceNamespace": "sts"}],
            }
        ]

        with mock.patch(
            "prowler.providers.aws.services.iam.iam_service.IAM", iam_client
        ):
            from prowler.providers.aws.services.iam.iam_use_temporary_credentials.iam_use_temporary_credentials import (
                iam_use_temporary_credentials,
            )

            check = iam_use_temporary_credentials()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"

    def test_access_keys_with_iam_and_sts(self):
        iam_client = mock.MagicMock
        iam_client.region = AWS_REGION
        iam_client.access_keys_metadata = [
            {"access_keys_metadata": [{"AccessKeyMetadata": [{"AK1": 1}]}]}
        ]
        iam_client.last_accessed_services = [
            {
                "user": User(
                    name="user1",
                    arn="user1-arn",
                    mfa_devices=[],
                    attached_policies=[],
                    inline_policies=[],
                ),
                "services": [{"ServiceNamespace": "iam"}, {"ServiceNamespace": "sts"}],
            }
        ]

        with mock.patch(
            "prowler.providers.aws.services.iam.iam_service.IAM", iam_client
        ):
            from prowler.providers.aws.services.iam.iam_use_temporary_credentials.iam_use_temporary_credentials import (
                iam_use_temporary_credentials,
            )

            check = iam_use_temporary_credentials()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"

    def test_access_keys_with_iam_and_others(self):
        iam_client = mock.MagicMock
        iam_client.region = AWS_REGION
        iam_client.access_keys_metadata = [
            {"access_keys_metadata": [{"AccessKeyMetadata": [{"AK1": 1}]}]}
        ]
        iam_client.last_accessed_services = [
            {
                "user": User(
                    name="user1",
                    arn="user1-arn",
                    mfa_devices=[],
                    attached_policies=[],
                    inline_policies=[],
                ),
                "services": [{"ServiceNamespace": "iam"}, {"ServiceNamespace": "ec2"}],
            }
        ]

        with mock.patch(
            "prowler.providers.aws.services.iam.iam_service.IAM", iam_client
        ):
            from prowler.providers.aws.services.iam.iam_use_temporary_credentials.iam_use_temporary_credentials import (
                iam_use_temporary_credentials,
            )

            check = iam_use_temporary_credentials()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"

    def test_access_keys_with_sts_and_others(self):
        iam_client = mock.MagicMock
        iam_client.region = AWS_REGION
        iam_client.access_keys_metadata = [
            {"access_keys_metadata": [{"AccessKeyMetadata": [{"AK1": 1}]}]}
        ]
        iam_client.last_accessed_services = [
            {
                "user": User(
                    name="user1",
                    arn="user1-arn",
                    mfa_devices=[],
                    attached_policies=[],
                    inline_policies=[],
                ),
                "services": [{"ServiceNamespace": "sts"}, {"ServiceNamespace": "ec2"}],
            }
        ]

        with mock.patch(
            "prowler.providers.aws.services.iam.iam_service.IAM", iam_client
        ):
            from prowler.providers.aws.services.iam.iam_use_temporary_credentials.iam_use_temporary_credentials import (
                iam_use_temporary_credentials,
            )

            check = iam_use_temporary_credentials()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"

    def test_access_keys_with_other_services_than_iam_or_sts(self):
        iam_client = mock.MagicMock
        iam_client.region = AWS_REGION
        iam_client.access_keys_metadata = [
            {"access_keys_metadata": [{"AccessKeyMetadata": [{"AK1": 1}]}]}
        ]
        iam_client.last_accessed_services = [
            {
                "user": User(
                    name="user1",
                    arn="user1-arn",
                    mfa_devices=[],
                    attached_policies=[],
                    inline_policies=[],
                ),
                "services": [
                    {"ServiceNamespace": "ec2"},
                ],
            }
        ]

        with mock.patch(
            "prowler.providers.aws.services.iam.iam_service.IAM", iam_client
        ):
            from prowler.providers.aws.services.iam.iam_use_temporary_credentials.iam_use_temporary_credentials import (
                iam_use_temporary_credentials,
            )

            check = iam_use_temporary_credentials()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"

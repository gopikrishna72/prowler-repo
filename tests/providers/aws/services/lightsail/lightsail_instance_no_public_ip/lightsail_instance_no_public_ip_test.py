from unittest.mock import MagicMock, patch

from prowler.providers.aws.services.lightsail.lightsail_service import (
    Instance,
    PortRange,
)
from tests.providers.aws.utils import (
    AWS_REGION_US_EAST_1,
    AWS_REGION_US_EAST_1_AZA,
    set_mocked_aws_provider,
)


class Test_lightsail_instance_public_ip:
    def test_no_instances(self):
        lightsail_client = MagicMock
        lightsail_client.instances = []

        with patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_aws_provider([AWS_REGION_US_EAST_1]),
        ), patch(
            "prowler.providers.aws.services.lightsail.lightsail_service.Lightsail",
            new=lightsail_client,
        ):
            from prowler.providers.aws.services.lightsail.lightsail_instance_no_public_ip.lightsail_instance_no_public_ip import (
                lightsail_instance_no_public_ip,
            )

            check = lightsail_instance_no_public_ip()
            result = check.execute()

            assert len(result) == 0

    def test_public_ip(self):
        lightsail_client = MagicMock
        lightsail_client.instances = [
            Instance(
                name="test-instance",
                arn=f"arn:aws:lightsail:{AWS_REGION_US_EAST_1}:123456789012:Instance/test-instance",
                tags=[],
                location={
                    "regionName": AWS_REGION_US_EAST_1,
                    "availabilityZone": AWS_REGION_US_EAST_1_AZA,
                },
                static_ip=False,
                public_ip="1.2.3.4",
                private_ip="10.0.0.2",
                ipv6_addresses=[],
                ip_address_type="ipv4",
                ports=[
                    PortRange(
                        range="80",
                        protocol="tcp",
                        access_from="0.0.0.0/0",
                        access_type="Public",
                    ),
                    PortRange(
                        range="443",
                        protocol="tcp",
                        access_from="0.0.0.0/0",
                        access_type="Public",
                    ),
                ],
                auto_snapshot=False,
            )
        ]

        with patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_aws_provider([AWS_REGION_US_EAST_1]),
        ), patch(
            "prowler.providers.aws.services.lightsail.lightsail_service.Lightsail",
            new=lightsail_client,
        ):
            from prowler.providers.aws.services.lightsail.lightsail_instance_no_public_ip.lightsail_instance_no_public_ip import (
                lightsail_instance_no_public_ip,
            )

            check = lightsail_instance_no_public_ip()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert (
                result[0].status_extended == "Instance test-instance has a public IP."
            )
            assert result[0].resource_id == "test-instance"
            assert (
                result[0].resource_arn
                == f"arn:aws:lightsail:{AWS_REGION_US_EAST_1}:123456789012:Instance/test-instance"
            )
            assert result[0].resource_tags == []
            assert result[0].region == AWS_REGION_US_EAST_1

    def test_no_public_ip(self):
        lightsail_client = MagicMock
        lightsail_client.instances = [
            Instance(
                name="test-instance",
                arn=f"arn:aws:lightsail:{AWS_REGION_US_EAST_1}:123456789012:Instance/test-instance",
                tags=[],
                location={
                    "regionName": AWS_REGION_US_EAST_1,
                    "availabilityZone": AWS_REGION_US_EAST_1_AZA,
                },
                static_ip=False,
                public_ip="",
                private_ip="172.16.1.3",
                ipv6_addresses=[],
                ip_address_type="ipv4",
                ports=[
                    PortRange(
                        range="80",
                        protocol="tcp",
                        access_from="",
                        access_type="Private",
                    ),
                    PortRange(
                        range="443",
                        protocol="tcp",
                        access_from="",
                        access_type="Private",
                    ),
                ],
                auto_snapshot=False,
            )
        ]

        with patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_aws_provider([AWS_REGION_US_EAST_1]),
        ), patch(
            "prowler.providers.aws.services.lightsail.lightsail_service.Lightsail",
            new=lightsail_client,
        ):
            from prowler.providers.aws.services.lightsail.lightsail_instance_no_public_ip.lightsail_instance_no_public_ip import (
                lightsail_instance_no_public_ip,
            )

            check = lightsail_instance_no_public_ip()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "PASS"
            assert (
                result[0].status_extended
                == "Instance test-instance does not have a public IP."
            )
            assert result[0].resource_id == "test-instance"
            assert (
                result[0].resource_arn
                == f"arn:aws:lightsail:{AWS_REGION_US_EAST_1}:123456789012:Instance/test-instance"
            )
            assert result[0].resource_tags == []
            assert result[0].region == AWS_REGION_US_EAST_1

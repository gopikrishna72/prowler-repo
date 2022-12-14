from re import search
from unittest import mock

from boto3 import client
from moto import mock_ec2

AWS_REGION = "us-east-1"


class Test_ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888:
    @mock_ec2
    def test_ec2_default_sgs(self):
        # Create EC2 Mocked Resources
        ec2_client = client("ec2", region_name=AWS_REGION)
        ec2_client.create_vpc(CidrBlock="10.0.0.0/16")

        from prowler.providers.aws.lib.audit_info.audit_info import current_audit_info
        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info.audited_partition = "aws"
        current_audit_info.audited_regions = ["eu-west-1", "us-east-1"]

        with mock.patch(
            "prowler.providers.aws.services.ec2.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888 import (
                ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888,
            )

            check = (
                ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888()
            )
            result = check.execute()

            # One default sg per region
            assert len(result) == 3
            # All are compliant by default
            assert result[0].status == "PASS"

    @mock_ec2
    def test_ec2_non_compliant_default_sg(self):
        # Create EC2 Mocked Resources
        ec2_client = client("ec2", region_name=AWS_REGION)
        ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
        default_sg_id = ec2_client.describe_security_groups(GroupNames=["default"])[
            "SecurityGroups"
        ][0]["GroupId"]
        ec2_client.authorize_security_group_ingress(
            GroupId=default_sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 7199,
                    "ToPort": 9160,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        )

        from prowler.providers.aws.lib.audit_info.audit_info import current_audit_info
        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info.audited_partition = "aws"
        current_audit_info.audited_regions = ["eu-west-1", "us-east-1"]

        with mock.patch(
            "prowler.providers.aws.services.ec2.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888 import (
                ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888,
            )

            check = (
                ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888()
            )
            result = check.execute()

            # One default sg per region
            assert len(result) == 3
            # Search changed sg
            for sg in result:
                if sg.resource_id == default_sg_id:
                    assert sg.status == "FAIL"
                    assert search(
                        "has Casandra ports 7199, 8888 and 9160 open to the Internet",
                        sg.status_extended,
                    )

    @mock_ec2
    def test_ec2_compliant_default_sg(self):
        # Create EC2 Mocked Resources
        ec2_client = client("ec2", region_name=AWS_REGION)
        ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
        default_sg_id = ec2_client.describe_security_groups(GroupNames=["default"])[
            "SecurityGroups"
        ][0]["GroupId"]
        ec2_client.authorize_security_group_ingress(
            GroupId=default_sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 7199,
                    "ToPort": 9160,
                    "IpRanges": [{"CidrIp": "123.123.123.123/32"}],
                }
            ],
        )

        from prowler.providers.aws.lib.audit_info.audit_info import current_audit_info
        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info.audited_partition = "aws"
        current_audit_info.audited_regions = ["eu-west-1", "us-east-1"]

        with mock.patch(
            "prowler.providers.aws.services.ec2.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888.ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888 import (
                ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888,
            )

            check = (
                ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_cassandra_7199_9160_8888()
            )
            result = check.execute()

            # One default sg per region
            assert len(result) == 3
            # Search changed sg
            for sg in result:
                if sg.resource_id == default_sg_id:
                    assert sg.status == "PASS"
                    assert search(
                        "has not Casandra ports 7199, 8888 and 9160 open to the Internet",
                        sg.status_extended,
                    )

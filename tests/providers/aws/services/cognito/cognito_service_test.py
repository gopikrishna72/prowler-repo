import mock
from boto3 import client
from moto import mock_aws

from prowler.providers.aws.services.cognito.cognito_service import (
    CognitoIDP,
    RiskConfiguration,
)
from tests.providers.aws.utils import (
    AWS_ACCOUNT_NUMBER,
    AWS_REGION_EU_WEST_1,
    AWS_REGION_US_EAST_1,
    set_mocked_aws_provider,
)


class Test_Cognito_Service:
    # Test Cognito Service
    @mock_aws
    def test_service(self):
        aws_provider = set_mocked_aws_provider(
            audited_regions=[AWS_REGION_EU_WEST_1, AWS_REGION_US_EAST_1]
        )
        cognito = CognitoIDP(aws_provider)
        assert cognito.service == "cognito-idp"

    # Test Cognito client
    @mock_aws
    def test_client(self):
        aws_provider = set_mocked_aws_provider(
            audited_regions=[AWS_REGION_EU_WEST_1, AWS_REGION_US_EAST_1]
        )
        cognito = CognitoIDP(aws_provider)
        for regional_client in cognito.regional_clients.values():
            assert regional_client.__class__.__name__ == "CognitoIdentityProvider"

    # Test Cognito session
    @mock_aws
    def test__get_session__(self):
        aws_provider = set_mocked_aws_provider(
            audited_regions=[AWS_REGION_EU_WEST_1, AWS_REGION_US_EAST_1]
        )
        cognito = CognitoIDP(aws_provider)
        assert cognito.session.__class__.__name__ == "Session"

    # Test Cognito Session
    @mock_aws
    def test_audited_account(self):
        aws_provider = set_mocked_aws_provider(
            audited_regions=[AWS_REGION_EU_WEST_1, AWS_REGION_US_EAST_1]
        )
        cognito = CognitoIDP(aws_provider)
        assert cognito.audited_account == AWS_ACCOUNT_NUMBER

    @mock_aws
    def test_list_user_pools(self):
        user_pool_name_1 = "user_pool_test_1"
        user_pool_name_2 = "user_pool_test_2"
        aws_provider = set_mocked_aws_provider(
            audited_regions=[AWS_REGION_EU_WEST_1, AWS_REGION_US_EAST_1]
        )
        cognito_client_eu_west_1 = client("cognito-idp", region_name="eu-west-1")
        cognito_client_us_east_1 = client("cognito-idp", region_name="us-east-1")
        cognito_client_eu_west_1.create_user_pool(PoolName=user_pool_name_1)
        cognito_client_us_east_1.create_user_pool(PoolName=user_pool_name_2)
        cognito = CognitoIDP(aws_provider)
        assert len(cognito.user_pools) == 2
        for user_pool in cognito.user_pools.values():
            assert (
                user_pool.name == user_pool_name_1 or user_pool.name == user_pool_name_2
            )
            assert user_pool.region == "eu-west-1" or user_pool.region == "us-east-1"

    @mock_aws
    def test_describe_user_pools(self):
        user_pool_name_1 = "user_pool_test_1"
        aws_provider = set_mocked_aws_provider(
            audited_regions=[AWS_REGION_EU_WEST_1, AWS_REGION_US_EAST_1]
        )
        cognito_client_eu_west_1 = client("cognito-idp", region_name="eu-west-1")
        user_pool_id = cognito_client_eu_west_1.create_user_pool(
            PoolName=user_pool_name_1
        )["UserPool"]["Id"]
        cognito = CognitoIDP(aws_provider)
        assert len(cognito.user_pools) == 1
        for user_pool in cognito.user_pools.values():
            assert user_pool.name == user_pool_name_1
            assert user_pool.region == "eu-west-1"
            assert user_pool.id == user_pool_id
            assert user_pool.password_policy is not None
            assert user_pool.deletion_protection is not None
            assert user_pool.advanced_security_mode is not None
            assert user_pool.tags is not None
            assert user_pool.account_recovery_settings is not None
            assert user_pool.user_pool_client is not None

    @mock_aws
    def test_get_user_pool_mfa_config(self):
        user_pool_name_1 = "user_pool_test_1"
        aws_provider = set_mocked_aws_provider(
            audited_regions=[AWS_REGION_EU_WEST_1, AWS_REGION_US_EAST_1]
        )
        cognito_client_eu_west_1 = client("cognito-idp", region_name="eu-west-1")
        user_pool_id = cognito_client_eu_west_1.create_user_pool(
            PoolName=user_pool_name_1
        )["UserPool"]["Id"]
        cognito_client_eu_west_1.set_user_pool_mfa_config(
            UserPoolId=user_pool_id,
            SoftwareTokenMfaConfiguration={"Enabled": True},
            MfaConfiguration="ON",
        )
        cognito = CognitoIDP(aws_provider)
        assert len(cognito.user_pools) == 1
        for user_pool in cognito.user_pools.values():
            assert user_pool.name == user_pool_name_1
            assert user_pool.region == "eu-west-1"
            assert user_pool.id == user_pool_id
            assert user_pool.mfa_config is not None
            assert user_pool.mfa_config.sms_authentication == {}
            assert user_pool.mfa_config.software_token_mfa_authentication == {
                "Enabled": True
            }
            assert user_pool.mfa_config.status == "ON"

    def test_get_user_pool_risk_configuration(self):
        cognito_client = mock.MagicMock()
        user_pool_arn = "user_pool_test_1"
        cognito_client.user_pools[user_pool_arn].id = "user_pool_id"
        cognito_client.user_pools[user_pool_arn].arn = user_pool_arn
        cognito_client.user_pools[user_pool_arn].name = "user_pool_name"
        cognito_client.user_pools[user_pool_arn].region = "eu-west-1"
        cognito_client.user_pools[user_pool_arn].risk_configuration = RiskConfiguration(
            compromised_credentials_risk_configuration={
                "EventFilter": ["PASSWORD_CHANGE", "SIGN_UP", "SIGN_IN"],
                "Actions": {"EventAction": "BLOCK"},
            },
            account_takeover_risk_configuration={
                "Actions": {
                    "LowAction": {"Notify": False, "EventAction": "BLOCK"},
                    "MediumAction": {"Notify": False, "EventAction": "BLOCK"},
                    "HighAction": {"Notify": False, "EventAction": "BLOCK"},
                }
            },
        )

        with mock.patch(
            "prowler.providers.common.common.get_global_provider",
            return_value=set_mocked_aws_provider(),
        ), mock.patch(
            "prowler.providers.aws.services.cognito.cognito_idp_client.cognito_idp_client",
            new=cognito_client,
        ):
            for user_pool in cognito_client.user_pools.values():
                assert user_pool.region == "eu-west-1"
                assert user_pool.name == "user_pool_name"
                assert user_pool.id == "user_pool_id"
                assert (
                    user_pool.risk_configuration.compromised_credentials_risk_configuration
                    == {
                        "EventFilter": ["PASSWORD_CHANGE", "SIGN_UP", "SIGN_IN"],
                        "Actions": {"EventAction": "BLOCK"},
                    }
                )
                assert (
                    user_pool.risk_configuration.account_takeover_risk_configuration
                    == {
                        "Actions": {
                            "LowAction": {"Notify": False, "EventAction": "BLOCK"},
                            "MediumAction": {"Notify": False, "EventAction": "BLOCK"},
                            "HighAction": {"Notify": False, "EventAction": "BLOCK"},
                        }
                    }
                )

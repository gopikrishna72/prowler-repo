from re import search
from unittest import mock

from providers.aws.services.opensearch.opensearch_service import OpenSearchDomain

AWS_REGION = "eu-west-1"
AWS_ACCOUNT_NUMBER = "123456789012"

domain_name = "test-domain"
domain_arn = f"arn:aws:es:us-west-2:{AWS_ACCOUNT_NUMBER}:domain/{domain_name}"


class Test_opensearch_service_domains_internal_user_database_enabled:
    def test_no_domains(self):
        opensearch_client = mock.MagicMock
        opensearch_client.opensearch_domains = []
        with mock.patch(
            "providers.aws.services.opensearch.opensearch_service.OpenSearchService",
            opensearch_client,
        ):
            from providers.aws.services.opensearch.opensearch_service_domains_internal_user_database_enabled.opensearch_service_domains_internal_user_database_enabled import (
                opensearch_service_domains_internal_user_database_enabled,
            )

            check = opensearch_service_domains_internal_user_database_enabled()
            result = check.execute()
            assert len(result) == 0

    def test_internal_database_disabled(self):
        opensearch_client = mock.MagicMock
        opensearch_client.opensearch_domains = []
        opensearch_client.opensearch_domains.append(
            OpenSearchDomain(
                name=domain_name,
                region=AWS_REGION,
                arn=domain_arn,
                internal_user_database=False,
            )
        )
        opensearch_client.opensearch_domains[0].logging = []

        with mock.patch(
            "providers.aws.services.opensearch.opensearch_service.OpenSearchService",
            opensearch_client,
        ):
            from providers.aws.services.opensearch.opensearch_service_domains_internal_user_database_enabled.opensearch_service_domains_internal_user_database_enabled import (
                opensearch_service_domains_internal_user_database_enabled,
            )

            check = opensearch_service_domains_internal_user_database_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert search(
                "does not have internal user database enabled",
                result[0].status_extended,
            )
            assert result[0].resource_id == domain_name
            assert result[0].resource_arn == domain_arn

    def test_internal_database_enabled(self):
        opensearch_client = mock.MagicMock
        opensearch_client.opensearch_domains = []
        opensearch_client.opensearch_domains.append(
            OpenSearchDomain(
                name=domain_name,
                region=AWS_REGION,
                arn=domain_arn,
                internal_user_database=True,
            )
        )
        opensearch_client.opensearch_domains[0].logging = []

        with mock.patch(
            "providers.aws.services.opensearch.opensearch_service.OpenSearchService",
            opensearch_client,
        ):
            from providers.aws.services.opensearch.opensearch_service_domains_internal_user_database_enabled.opensearch_service_domains_internal_user_database_enabled import (
                opensearch_service_domains_internal_user_database_enabled,
            )

            check = opensearch_service_domains_internal_user_database_enabled()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert search(
                "has internal user database enabled", result[0].status_extended
            )
            assert result[0].resource_id == domain_name
            assert result[0].resource_arn == domain_arn

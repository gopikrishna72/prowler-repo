from re import search
from unittest import mock

from providers.aws.services.eks.eks_service import EKSCluster

AWS_REGION = "eu-west-1"
AWS_ACCOUNT_NUMBER = "123456789012"

cluster_name = "cluster_test"
cluster_arn = f"arn:aws:eks:{AWS_REGION}:{AWS_ACCOUNT_NUMBER}:cluster/{cluster_name}"


class Test_eks_endpoints_not_publicly_accessible:
    def test_no_clusters(self):
        eks_client = mock.MagicMock
        eks_client.clusters = []
        with mock.patch(
            "providers.aws.services.eks.eks_service.EKS",
            eks_client,
        ):
            from providers.aws.services.eks.eks_endpoints_not_publicly_accessible.eks_endpoints_not_publicly_accessible import (
                eks_endpoints_not_publicly_accessible,
            )

            check = eks_endpoints_not_publicly_accessible()
            result = check.execute()
            assert len(result) == 0

    def test_endpoint_public_access(self):
        eks_client = mock.MagicMock
        eks_client.clusters = []
        eks_client.clusters.append(
            EKSCluster(
                name=cluster_name,
                arn=cluster_arn,
                region=AWS_REGION,
                logging=None,
                endpoint_public_access=True,
                endpoint_private_access=False,
            )
        )

        with mock.patch(
            "providers.aws.services.eks.eks_service.EKS",
            eks_client,
        ):
            from providers.aws.services.eks.eks_endpoints_not_publicly_accessible.eks_endpoints_not_publicly_accessible import (
                eks_endpoints_not_publicly_accessible,
            )

            check = eks_endpoints_not_publicly_accessible()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert search(
                "Cluster endpoint access is public for EKS cluster",
                result[0].status_extended,
            )
            assert result[0].resource_id == cluster_name
            assert result[0].resource_arn == cluster_arn

    def test_endpoint_not_public_access(self):
        eks_client = mock.MagicMock
        eks_client.clusters = []
        eks_client.clusters.append(
            EKSCluster(
                name=cluster_name,
                arn=cluster_arn,
                region=AWS_REGION,
                logging=None,
                endpoint_public_access=False,
                endpoint_private_access=True,
            )
        )

        with mock.patch(
            "providers.aws.services.eks.eks_service.EKS",
            eks_client,
        ):
            from providers.aws.services.eks.eks_endpoints_not_publicly_accessible.eks_endpoints_not_publicly_accessible import (
                eks_endpoints_not_publicly_accessible,
            )

            check = eks_endpoints_not_publicly_accessible()
            result = check.execute()
            assert len(result) == 1
            assert result[0].status == "PASS"
            assert search(
                "Cluster endpoint access is private for EKS cluster",
                result[0].status_extended,
            )
            assert result[0].resource_id == cluster_name
            assert result[0].resource_arn == cluster_arn

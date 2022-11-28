from datetime import datetime, timezone

from lib.check.models import Check, Check_Report
from providers.aws.services.iam.iam_client import iam_client


class iam_no_expired_server_certificates_stored(Check):
    def execute(self) -> Check_Report:
        findings = []

        for certificate in iam_client.server_certificates:
            report = Check_Report(self.metadata())
            report.region = iam_client.region
            report.resource_id = certificate.id
            report.resource_arn = certificate.arn
            expiration_days = (datetime.now(timezone.utc) - certificate.expiration).days
            if expiration_days >= 0:
                report.status = "FAIL"
                report.status_extended = f"IAM Certificate {certificate.name} has expired {expiration_days} days ago."
            else:
                report.status = "PASS"
                report.status_extended = (
                    f"IAM Certificate {certificate.name} is not expired."
                )
            findings.append(report)

        return findings

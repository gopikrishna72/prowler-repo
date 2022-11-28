from lib.check.models import Check, Check_Report
from providers.aws.services.globalaccelerator.globalaccelerator_client import (
    globalaccelerator_client,
)
from providers.aws.services.shield.shield_client import shield_client


class shield_advanced_protection_in_global_accelerators(Check):
    def execute(self):
        findings = []
        if shield_client.enabled:
            for accelerator in globalaccelerator_client.accelerators.values():
                report = Check_Report(self.metadata())
                report.region = shield_client.region
                report.resource_id = accelerator.name
                report.resource_arn = accelerator.arn
                report.status = "FAIL"
                report.status_extended = f"Global Accelerator {accelerator.name} is not protected by AWS Shield Advanced"

                for protection in shield_client.protections.values():
                    if accelerator.arn == protection.resource_arn:
                        report.status = "PASS"
                        report.status_extended = f"Global Accelerator {accelerator.name} is protected by AWS Shield Advanced"
                        break

                findings.append(report)

        return findings

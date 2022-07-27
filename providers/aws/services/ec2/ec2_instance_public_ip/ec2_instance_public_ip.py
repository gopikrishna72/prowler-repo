from lib.check.models import Check, Check_Report
from providers.aws.services.ec2.ec2_service import ec2_client


class ec2_instance_public_ip(Check):
    def execute(self):
        findings = []
        for instance in ec2_client.instances:
            report = Check_Report(self.metadata)
            report.region = instance.region
            if instance.public_ip:
                report.status = "FAIL"
                report.status_extended = f"EC2 instance {instance.id} has a Public IP: {instance.public_ip} ({instance.public_dns})."
                report.resource_id = {instance.id}
            else:
                report.status = "PASS"
                report.status_extended = (
                    f"EC2 instance {instance.id} has not a Public IP."
                )
                report.resource_id = {instance.id}
            findings.append(report)

        return findings

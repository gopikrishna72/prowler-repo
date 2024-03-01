from prowler.lib.check.models import Check, Check_Report_Azure
from prowler.providers.azure.services.monitor.monitor_client import monitor_client
from prowler.providers.azure.services.storage.storage_client import storage_client


class monitor_storage_account_with_activity_logs_cmk_encrypted(Check):
    def execute(self) -> Check_Report_Azure:
        findings = []

        for (
            subscription_name,
            diagnostic_settings,
        ) in monitor_client.diagnostics_settings.items():
            if not diagnostic_settings:
                report = Check_Report_Azure(self.metadata())
                report.subscription = subscription_name
                report.resource_name = "Monitor"
                report.resource_id = "Monitor"
                report.status = "PASS"
                report.status_extended = f"Encryption with CMK in subscription {subscription_name} is not necessary."
                findings.append(report)

            for diagnostic_setting in diagnostic_settings:
                sa_id = diagnostic_setting.storage_account_id  # sa = storage account
                elements = sa_id.split("/")
                sa_name = elements[8]
                for storage_account in storage_client.storage_accounts[
                    subscription_name
                ]:
                    if storage_account.name == sa_name:
                        report = Check_Report_Azure(self.metadata())
                        report.subscription = subscription_name
                        report.resource_name = "Monitor"
                        report.resource_id = "Monitor"
                        if storage_account.encryption_type == "Microsoft.Storage":
                            report.status = "FAIL"
                            report.status_extended = f"Storage account {storage_account.name} storing activity log in subscription {subscription_name} is not encrypted with Customer Managed Key."
                            findings.append(report)
                        else:
                            report.status = "PASS"
                            report.status_extended = f"Storage account {storage_account.name} storing activity log in subscription {subscription_name} is encrypted with Customer Managed Key or not necessary."
                            findings.append(report)

        return findings

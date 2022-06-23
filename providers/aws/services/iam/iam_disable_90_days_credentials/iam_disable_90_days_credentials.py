from datetime import datetime

from lib.check.models import Check, Check_Report
from providers.aws.services.iam.iam_service import iam_client

maximum_expiration_days = 90


class iam_disable_90_days_credentials(Check):
    def execute(self) -> Check_Report:
        findings = []
        response = iam_client.users

        if response:
            for user in response:
                report = Check_Report(self.metadata)
                if "PasswordLastUsed" in user and user["PasswordLastUsed"] != "":
                    try:
                        time_since_insertion = (
                            datetime.datetime.now(datetime.timezone.utc)
                            - user["PasswordLastUsed"]
                        )
                        if time_since_insertion.days > maximum_expiration_days:
                            report.status = "FAIL"
                            report.result_extended = f"User {user['UserName']} has not logged into the console in the past 90 days"
                            report.region = "us-east-1"
                        else:
                            report.status = "PASS"
                            report.result_extended = f"User {user['UserName']} has logged into the console in the past 90 days"
                            report.region = "us-east-1"
                    except KeyError:
                        pass
                else:
                    report.status = "PASS"
                    report.result_extended = f"User {user['UserName']} has not a console password or is unused."
                    report.region = "us-east-1"

                # Append report
                findings.append(report)
        else:
            report = Check_Report(self.metadata)
            report.status = "PASS"
            report.result_extended = "There is no IAM users"
            report.region = "us-east-1"

        return findings

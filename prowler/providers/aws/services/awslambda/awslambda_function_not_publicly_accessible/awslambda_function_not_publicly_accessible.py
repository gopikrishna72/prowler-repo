from prowler.lib.check.models import Check, Check_Report_AWS
from prowler.providers.aws.services.awslambda.awslambda_client import awslambda_client

class awslambda_function_serverless_architecture(Check):
    """awslambda_function_serverless_architecture verifies if an AWS Lambda function uses a serverless architecture"""

    def execute(self):
        findings = []

        for lambda_function in awslambda_client.functions:
            report = Check_Report_AWS(self.metadata())

            report.region = lambda_function.region
            report.resource_id = lambda_function.name
            report.resource_arn = lambda_function.arn
            report.resource_tags = lambda_function.tags

            report.status = "PASS"
            report.status_extended = f"AWS Lambda function {lambda_function.name} is not using a serverless architecture."

            # Check if the Lambda function is part of an AWS SAM deployment
            if "AWS::Serverless" in lambda_function.resource_type:
                report.status = "FAIL"
                report.status_extended = f"AWS Lambda function {lambda_function.name} is using a serverless architecture."

            findings.append(report)

        return findings

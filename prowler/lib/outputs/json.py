import os
import sys

from prowler.config.config import (
    json_asff_file_suffix,
    json_file_suffix,
    json_ocsf_file_suffix,
    prowler_version,
    timestamp_utc,
)
from prowler.lib.logger import logger
from prowler.lib.outputs.models import (
    Account,
    Check_Output_JSON_OCSF,
    Compliance,
    Group,
    Organization,
    ProductFields,
    Resource,
    Resources,
    Severity,
    get_check_compliance,
)
from prowler.lib.utils.utils import hash_sha512, open_file


def fill_json_asff(finding_output, audit_info, finding, output_options):
    # Check if there are no resources in the finding
    if finding.resource_arn == "":
        if finding.resource_id == "":
            finding.resource_id = "NONE_PROVIDED"
        finding.resource_arn = finding.resource_id
    finding_output.Id = f"prowler-{finding.check_metadata.CheckID}-{audit_info.audited_account}-{finding.region}-{hash_sha512(finding.resource_id)}"
    finding_output.ProductArn = f"arn:{audit_info.audited_partition}:securityhub:{finding.region}::product/prowler/prowler"
    finding_output.ProductFields = ProductFields(
        ProviderVersion=prowler_version, ProwlerResourceName=finding.resource_arn
    )
    finding_output.GeneratorId = "prowler-" + finding.check_metadata.CheckID
    finding_output.AwsAccountId = audit_info.audited_account
    finding_output.Types = finding.check_metadata.CheckType
    finding_output.FirstObservedAt = (
        finding_output.UpdatedAt
    ) = finding_output.CreatedAt = timestamp_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    finding_output.Severity = Severity(Label=finding.check_metadata.Severity.upper())
    finding_output.Title = finding.check_metadata.CheckTitle
    finding_output.Description = finding.status_extended
    finding_output.Resources = [
        Resource(
            Id=finding.resource_arn,
            Type=finding.check_metadata.ResourceType,
            Partition=audit_info.audited_partition,
            Region=finding.region,
        )
    ]
    # Iterate for each compliance framework
    compliance_summary = []
    associated_standards = []
    check_compliance = get_check_compliance(finding, "aws", output_options)
    for key, value in check_compliance.items():
        associated_standards.append({"StandardsId": key})
        item = f"{key} {' '.join(value)}"
        if len(item) > 64:
            item = item[0:63]
        compliance_summary.append(item)

    # Add ED to PASS or FAIL (PASSED/FAILED)
    finding_output.Compliance = Compliance(
        Status=finding.status + "ED",
        AssociatedStandards=associated_standards,
        RelatedRequirements=compliance_summary,
    )
    finding_output.Remediation = {
        "Recommendation": finding.check_metadata.Remediation.Recommendation
    }

    return finding_output


def fill_json_ocsf(
    finding_output: Check_Output_JSON_OCSF, audit_info, finding, output_options
):
    finding_output.finding.title = (
        finding_output.metadata.product.feature.uid
    ) = finding.check_metadata.CheckType
    finding_output.resources.append(
        Resources(
            group=Group(name=finding.check_metadata.ServiceName),
        )
    )
    if finding.status == "PASS":
        finding_output.status = finding_output.compliance.status = "Success"
        finding_output.status_id = 1
    elif finding.status == "FAIL":
        finding_output.status = finding_output.compliance.status = "Failure"
        finding_output.status_id = 2
    finding_output.status_detail = finding_output.message = finding.status_extended
    finding_output.severity = finding.check_metadata.Severity
    if finding_output.severity == "low":
        finding_output.severity_id = 2
    elif finding_output.severity == "medium":
        finding_output.severity_id = 3
    elif finding_output.severity == "high":
        finding_output.severity_id = 4
    elif finding_output.severity == "critical":
        finding_output.severity_id = 5
    if audit_info.organizations_metadata:
        aws_account_name = audit_info.organizations_metadata.account_details_name
        aws_org_uid = audit_info.organizations_metadata.account_details_org
    if finding.check_metadata.Provider == "aws":
        finding_output.cloud.account = Account(
            name=aws_account_name,
            uid=audit_info.audited_account,
        )
        finding_output.cloud.org = Organization(
            name="",
            uid=aws_org_uid,
        )
    elif finding.check_metadata.Provider == "azure":
        finding_output.cloud.account = Account(
            name=finding.subscription,
            uid=finding.subscription,
        )
        finding_output.cloud.org = Organization(
            name="",
            uid=audit_info.identity.domain,
        )
    elif finding.check_metadata.Provider == "gcp":
        finding_output.cloud.account = None
        finding_output.cloud.org = None
    # Region (AWS)

    return finding_output


def close_json(output_filename, output_directory, mode):
    """close_json closes the output JSON file replacing the last comma with ]"""
    try:
        suffix = json_file_suffix
        if mode == "json-asff":
            suffix = json_asff_file_suffix
        elif mode == "json-ocsf":
            suffix = json_ocsf_file_suffix
        filename = f"{output_directory}/{output_filename}{suffix}"
        # Close JSON file if exists
        if os.path.isfile(filename):
            file_descriptor = open_file(
                filename,
                "a",
            )
            # Replace last comma for square bracket if not empty
            if file_descriptor.tell() > 0:
                if file_descriptor.tell() != 1:
                    file_descriptor.seek(file_descriptor.tell() - 1, os.SEEK_SET)
                file_descriptor.truncate()
                file_descriptor.write("]")
            file_descriptor.close()
    except Exception as error:
        logger.critical(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}] -- {error}"
        )
        sys.exit(1)

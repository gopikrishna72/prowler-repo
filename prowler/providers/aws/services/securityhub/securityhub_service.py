import threading
from dataclasses import dataclass

from botocore.client import ClientError

from prowler.lib.logger import logger
from prowler.lib.scan_filters.scan_filters import is_resource_filtered
from prowler.providers.aws.aws_provider import generate_regional_clients


################## SecurityHub
class SecurityHub:
    def __init__(self, audit_info):
        self.service = "securityhub"
        self.session = audit_info.audit_session
        self.audited_account = audit_info.audited_account
        self.audit_resources = audit_info.audit_resources
        self.regional_clients = generate_regional_clients(self.service, audit_info)
        self.securityhubs = []
        self.__threading_call__(self.__describe_hub__)

    def __get_session__(self):
        return self.session

    def __threading_call__(self, call):
        threads = []
        for regional_client in self.regional_clients.values():
            threads.append(threading.Thread(target=call, args=(regional_client,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def __describe_hub__(self, regional_client):
        logger.info("SecurityHub - Describing Hub...")
        try:
            # Check if SecurityHub is active
            try:
                hub_arn = regional_client.describe_hub()["HubArn"]
            except ClientError as e:
                # Check if Account is subscribed to Security Hub
                if e.response["Error"]["Code"] == "InvalidAccessException":
                    self.securityhubs.append(
                        SecurityHubHub(
                            "",
                            "Security Hub",
                            "NOT_AVAILABLE",
                            "",
                            "",
                            regional_client.region,
                        )
                    )
            else:
                if not self.audit_resources or (
                    is_resource_filtered(hub_arn, self.audit_resources)
                ):
                    hub_id = hub_arn.split("/")[1]
                    get_enabled_standards_paginator = regional_client.get_paginator(
                        "get_enabled_standards"
                    )
                    standards = ""
                    for page in get_enabled_standards_paginator.paginate():
                        for standard in page["StandardsSubscriptions"]:
                            standards += f"{standard['StandardsArn'].split('/')[1]} "
                    list_enabled_products_for_import_paginator = (
                        regional_client.get_paginator(
                            "list_enabled_products_for_import"
                        )
                    )
                    integrations = ""
                    for page in list_enabled_products_for_import_paginator.paginate():
                        for integration in page["ProductSubscriptions"]:
                            if (
                                "/aws/securityhub" not in integration
                            ):  # ignore Security Hub integration with itself
                                integrations += f"{integration.split('/')[-1]} "
                    self.securityhubs.append(
                        SecurityHubHub(
                            hub_arn,
                            hub_id,
                            "ACTIVE",
                            standards,
                            integrations,
                            regional_client.region,
                        )
                    )
                else:
                    # SecurityHub is filtered
                    self.securityhubs.append(
                        SecurityHubHub(
                            "",
                            "Security Hub",
                            "NOT_AVAILABLE",
                            "",
                            "",
                            regional_client.region,
                        )
                    )

        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )


@dataclass
class SecurityHubHub:
    arn: str
    id: str
    status: str
    standards: str
    integrations: str
    region: str

    def __init__(
        self,
        arn,
        id,
        status,
        standards,
        integrations,
        region,
    ):
        self.arn = arn
        self.id = id
        self.status = status
        self.standards = standards
        self.integrations = integrations
        self.region = region

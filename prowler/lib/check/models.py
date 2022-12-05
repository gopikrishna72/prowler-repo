import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass

from lib.logger import logger
from pydantic import BaseModel, ValidationError


@dataclass
class Output_From_Options:
    """Class to store the Prowler output modes options"""

    is_quiet: bool
    output_modes: list
    output_directory: str
    security_hub_enabled: bool
    output_filename: str
    allowlist_file: str
    bulk_checks_metadata: dict
    verbose: str


class Code(BaseModel):
    """Check's remediation information using IaC like CloudFormation, Terraform or the native CLI"""

    NativeIaC: str
    Terraform: str
    CLI: str
    Other: str


class Recommendation(BaseModel):
    """Check's recommendation information"""

    Text: str
    Url: str


class Remediation(BaseModel):
    """Check's remediation: Code and Recommendation"""

    Code: Code
    Recommendation: Recommendation


class Check_Metadata_Model(BaseModel):
    """Check Metadata Model"""

    Provider: str
    CheckID: str
    CheckTitle: str
    CheckType: list[str]
    ServiceName: str
    SubServiceName: str
    ResourceIdTemplate: str
    Severity: str
    ResourceType: str
    Description: str
    Risk: str
    RelatedUrl: str
    Remediation: Remediation
    Categories: list[str]
    Tags: dict
    DependsOn: list[str]
    RelatedTo: list[str]
    Notes: str
    # We set the compliance to None to
    # store the compliance later if supplied
    Compliance: list = None


class Check(ABC, Check_Metadata_Model):
    """Prowler Check"""

    def __init__(self, **data):
        """Check's init function. Calls the CheckMetadataModel init."""
        # Parse the Check's metadata file
        check_path_name = self.__class__.__module__.replace(".", "/")
        metadata_file = f"prowler/{check_path_name}.metadata.json"
        # Store it to validate them with Pydantic
        data = Check_Metadata_Model.parse_file(metadata_file).dict()
        # Calls parents init function
        super().__init__(**data)

    def metadata(self) -> dict:
        """Return the JSON representation of the check's metadata"""
        return self.json()

    @abstractmethod
    def execute(self):
        """Execute the check's logic"""


@dataclass
class Check_Report:
    """Contains the Check's finding information."""

    status: str
    region: str
    status_extended: str
    check_metadata: Check_Metadata_Model
    resource_id: str
    resource_details: str
    resource_tags: list
    resource_arn: str

    def __init__(self, metadata):
        self.check_metadata = Check_Metadata_Model.parse_raw(metadata)
        self.status_extended = ""
        self.resource_details = ""
        self.resource_tags = []
        self.resource_id = ""
        self.resource_arn = ""


# Testing Pending
def load_check_metadata(metadata_file: str) -> Check_Metadata_Model:
    """load_check_metadata loads and parse a Check's metadata file"""
    try:
        check_metadata = Check_Metadata_Model.parse_file(metadata_file)
    except ValidationError as error:
        logger.critical(f"Metadata from {metadata_file} is not valid: {error}")
        sys.exit()
    else:
        return check_metadata

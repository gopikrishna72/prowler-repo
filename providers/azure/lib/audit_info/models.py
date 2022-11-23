from dataclasses import dataclass

from azure.identity import DefaultAzureCredential
from pydantic import BaseModel


class Azure_Identity_Info(BaseModel):
    id: str = None
    app_id: str = None
    tenant_id: str = None


class Azure_Subscription(BaseModel):
    id: str = None
    display_name: str = None


@dataclass
class Azure_Audit_Info:
    credentials: DefaultAzureCredential
    identity: Azure_Identity_Info
    subscriptions: list[Azure_Subscription]

    def __init__(self, credentials, identity, subscriptions):
        self.credentials = credentials
        self.identity = identity
        self.subscriptions = subscriptions

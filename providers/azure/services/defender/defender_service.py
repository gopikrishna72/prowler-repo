from datetime import timedelta

from azure.mgmt.security import SecurityCenter
from pydantic import BaseModel

from lib.logger import logger


########################## Defender
class Defender:
    def __init__(self, audit_info):
        self.service = "defender"
        self.credentials = audit_info.credentials
        self.subscriptions = audit_info.subscriptions
        self.clients = self.__set_clients__(
            audit_info.subscriptions, audit_info.credentials
        )
        self.pricings = self.__get_pricings__()
        self.region = "azure"

    def __set_clients__(self, subscriptions, credentials):
        clients = {}
        try:
            for display_name, id in subscriptions.items():
                clients.update(
                    {
                        display_name: SecurityCenter(
                            credential=credentials, subscription_id=id
                        )
                    }
                )
        except Exception as error:
            logger.error(
                f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )
        else:
            return clients

    def __get_pricings__(self):
        logger.info("Defender - Getting pricings...")
        pricings = {}
        try:
            for subscription, client in self.clients.items():
                pricings_list = client.pricings.list()
                for pricing in pricings_list.value:
                    pricings.update(
                        {
                            subscription: Defender_Pricing(
                                name=pricing.name,
                                pricing_tier=pricing.pricing_tier,
                                free_trial_remaining_time=pricing.free_trial_remaining_time,
                            )
                        }
                    )
        except Exception as error:
            logger.error(
                f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )
        else:
            return pricings


class Defender_Pricing(BaseModel):
    name: str
    pricing_tier: str
    free_trial_remaining_time: timedelta

from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.redshift.redshift_service import Redshift

redshift_client = Redshift(current_audit_info)

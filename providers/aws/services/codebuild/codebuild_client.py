from providers.aws.lib.audit_info.audit_info import current_audit_info
from providers.aws.services.codebuild.codebuild_service import Codebuild

codebuild_client = Codebuild(current_audit_info)

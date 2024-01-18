import yaml

from prowler.lib.check.models import Check, Check_Report_Kubernetes
from prowler.providers.kubernetes.services.kubelet.kubelet_client import kubelet_client


class kubelet_manage_iptables(Check):
    def execute(self) -> Check_Report_Kubernetes:
        findings = []
        for cm in kubelet_client.kubelet_config_maps:
            arguments = yaml.safe_load(cm.data["kubelet"])
            report = Check_Report_Kubernetes(self.metadata())
            report.namespace = cm.namespace
            report.resource_name = cm.name
            report.resource_id = cm.uid
            if "makeIPTablesUtilChains" not in arguments:
                report.status = "MANUAL"
                report.status_extended = f"Kubelet does not have the argument `makeIPTablesUtilChains` in config file {cm.name}, verify it in the node's arguments."
            else:
                if arguments["makeIPTablesUtilChains"]:
                    report.status = "PASS"
                    report.status_extended = f"Kubelet is configured to manage iptables in config file {cm.name}."
                else:
                    report.status = "FAIL"
                    report.status_extended = f"Kubelet is not configured to manage iptables in config file {cm.name}."
            findings.append(report)
        return findings

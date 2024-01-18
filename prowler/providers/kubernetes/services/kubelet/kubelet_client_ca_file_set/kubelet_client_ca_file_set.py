import yaml

from prowler.lib.check.models import Check, Check_Report_Kubernetes
from prowler.providers.kubernetes.services.kubelet.kubelet_client import kubelet_client


class kubelet_client_ca_file_set(Check):
    def execute(self) -> Check_Report_Kubernetes:
        findings = []
        for cm in kubelet_client.kubelet_config_maps:
            authentication = yaml.safe_load(cm.data["kubelet"])["authentication"]
            report = Check_Report_Kubernetes(self.metadata())
            report.namespace = cm.namespace
            report.resource_name = cm.name
            report.resource_id = cm.uid
            report.status = "FAIL"
            report.status_extended = (
                f"Kubelet is missing the client CA file in config file {cm.name}."
            )
            if "clientCAFile" in authentication["x509"]:
                report.status = "PASS"
                report.status_extended = f"Kubelet has the client CA file configured appropriately in config file {cm.name}."
            findings.append(report)
        return findings

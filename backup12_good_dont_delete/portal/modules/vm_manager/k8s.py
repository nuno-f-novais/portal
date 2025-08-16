"""
VM management skeleton for OpenShift/KubeVirt, strictly adhering to the project memo.

Notes:
- This is a stub-only implementation. Fill in each function with real K8s/KubeVirt/OCP
  API calls as you wire up the backend. Function names, parameters, and control flow
  are designed to make it easy to remain compliant with the memo.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List
import subprocess

# ---------- Enums ----------
class CreateStatus(Enum):
    SUCCESS = "SUCCESS"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    FAILURE = "FAILURE"

# ---------- Public API (called by the Flask routes) ----------
def create_vm_with_templates(
    name: str,
    os_type: str,
    namespace: str = "poc-vms",
    source_pvc: Optional[str] = None,
    extra_disks: Optional[List[Dict[str, Any]]] = None,
) -> CreateStatus:
    """
    Create a VM according to the memo. Implementation outline only:
    1) Ensure namespace exists.
    2) Prepare/clone PVCs (support using `source_pvc` as rootdisk).
    3) Build VM spec with proper boot order (Windows ISO first -> rootdisk; Linux containerDisk).
    4) Create VM and wait for it to be Running.
    5) Generate Ansible inventory dynamically.
    6) Configure IP/network via Ansible after the VM is ready.
    7) Remove ISO and fix boot order, then reboot.
    8) Rollback PVCs on failure and return CreateStatus.
    """
    try:
        ensure_namespace(namespace)
        root_pvc = clone_pvc(namespace, source_pvc) if source_pvc else ensure_root_pvc(namespace, name)

        vm_spec = build_vm_spec(name=name, os_type=os_type, namespace=namespace, root_pvc=root_pvc, extra_disks=extra_disks)
        apply_vm(vm_spec)

        wait_for_vm_running(name=name, namespace=namespace)

        generate_inventory(name=name, namespace=namespace)

        # Configure network only AFTER VM is running
        configure_network()

        # Detach ISO (if any) and prioritize rootdisk
        remove_iso(name=name, namespace=namespace)
        fix_boot_order(name=name, namespace=namespace)

        return CreateStatus.SUCCESS
    except AlreadyExists:
        return CreateStatus.ALREADY_EXISTS
    except Exception as exc:
        # Roll back PVCs created during this flow
        rollback_pvcs_for_vm(namespace, name)
        return CreateStatus.FAILURE

# ---------- Skeleton helpers & required functions per memo ----------
class AlreadyExists(Exception):
    """Raised when the VM already exists."""

def ensure_namespace(namespace: str) -> None:
    """Create namespace `poc-vms` if needed."""
    # TODO: implement `oc`/k8s API call

def ensure_root_pvc(namespace: str, name: str) -> str:
    """Create or ensure a root PVC exists and return its name."""
    # TODO: implement
    return f"{name}-rootdisk"

def clone_pvc(namespace: str, source_pvc: str) -> str:
    """
    Clone an existing PVC to become the rootdisk, with proper error handling.
    Must support VolumeSnapshot/CSI cloning and return the new PVC name.
    """
    # TODO: implement cloning logic, raise on failure
    return f"{source_pvc}-clone"

def build_vm_spec(name: str, os_type: str, namespace: str, root_pvc: str, extra_disks=None) -> Dict[str, Any]:
    """
    Build the VM definition with correct disks and **full bootOrder** set on each disk.
    - Windows first boot: ISO (bootOrder: 1, cdrom: {bus: sata}) then rootdisk (bootOrder: 2).
    - Linux boot: containerDisk for installation with rootdisk as boot target.
    """
    # TODO: implement spec dict
    return {"metadata": {"name": name, "namespace": namespace}, "spec": {"osType": os_type, "rootPVC": root_pvc}}

def apply_vm(vm_spec: Dict[str, Any]) -> None:
    """Apply the VM spec to the cluster. Validate disks/volumes uniqueness and names."""
    # TODO: implement: kubernetes client or `oc apply`

def wait_for_vm_running(name: str, namespace: str) -> None:
    """
    Poll VM status until Running. Ensure Windows & Linux are fully booted
    before detaching ISO and before running Ansible.
    """
    # TODO: implement polling

def get_cloud_init(os_type: str) -> Dict[str, Any]:
    """
    Provide Cloud-Init (Linux) and unattend.xml (Windows) with VirtIO driver install and RDP/firewall.
    For Windows, the unattend.xml must go into a Secret referenced via userDataSecretRef.
    """
    # TODO: build both variants
    return {}

def generate_inventory(name: str, namespace: str) -> None:
    """
    Dynamically retrieve VM IPs (primary + pod network) and write a proper Ansible inventory file.
    Must be called BEFORE `configure_network()`.
    """
    # TODO: implement using kubernetes APIs

def configure_network() -> None:
    """
    Execute the Ansible playbook for network configuration.
    Must use subprocess.run and rely on the previously generated inventory.
    """
    subprocess.run(["ansible-playbook", "-i", "inventory.yml", "network_config.yml"], check=True)

def remove_iso(name: str, namespace: str) -> None:
    """
    After first boot, verify disks and remove ISO. Rebuild disk configuration based on creation parameters.
    Must be invoked after `wait_for_vm_running()`.
    """
    # TODO: implement

def fix_boot_order(name: str, namespace: str) -> None:
    """
    Ensure `rootdisk` is prioritized after installation and all disks have bootOrder.
    """
    # TODO: implement

def rollback_pvcs_for_vm(namespace: str, name: str) -> None:
    """Delete any PVCs created during a failed creation attempt (with clear logs)."""
    # TODO: implement

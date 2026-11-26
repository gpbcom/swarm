variable "machines" {
  description = "The machines given by the person, in order. Each has a unique name, a unique address and a role, server or agent. At least one must be a server."
  type = list(object({
    name    = string
    address = string
    role    = string
  }))

  validation {
    condition     = length([for m in var.machines : m if m.role == "server"]) >= 1
    error_message = "At least one machine must have the role server."
  }
}

variable "ssh_user" {
  description = "The user that Terraform connects as over SSH. It must be able to run sudo without a password."
  type        = string
}

variable "ssh_private_key_path" {
  description = "The path to the SSH private key file, kept outside the repository. Never the content of the key."
  type        = string
}

variable "k3s_version" {
  description = "The pinned k3s release to install, such as v1.31.4+k3s1."
  type        = string
}

variable "kubeconfig_path" {
  description = "Where the kubeconfig is written, outside the repository."
  type        = string
}

variable "api_allowed_cidrs" {
  description = "The CIDRs, besides the cell machines, allowed to reach the Kubernetes API on 6443/tcp."
  type        = list(string)
  default     = []
}

variable "object_storage_enabled" {
  description = "Whether the cell creates its buckets on a MinIO endpoint."
  type        = bool
  default     = false
}

variable "object_storage_endpoint" {
  description = "The MinIO endpoint as host:port. The credentials come from the provider's environment variables, never from a variable."
  type        = string
  default     = ""
}

variable "object_storage_buckets" {
  description = "The names of the buckets to create when object storage is enabled."
  type        = list(string)
  default     = []
}

variable "dns_enabled" {
  description = "Whether the cell writes its DNS records with RFC 2136 updates."
  type        = bool
  default     = false
}

variable "dns_server" {
  description = "The address of the DNS server that accepts updates. The TSIG key comes from the provider's environment variables, never from a variable."
  type        = string
  default     = ""
}

variable "dns_zone" {
  description = "The DNS zone the records are written to, fully qualified with a trailing dot."
  type        = string
  default     = ""
}

variable "platform_enabled" {
  description = "Whether the cell installs Argo CD and the root Application platform. Enable it on a second apply, once the first one has built the cluster and written the kubeconfig."
  type        = bool
  default     = false
}

variable "identity_enabled" {
  description = "Whether the cell deploys the identity of the global layer (Keycloak). It needs the platform, so enable it on a second apply, once platform_enabled is true."
  type        = bool
  default     = false

  validation {
    condition     = !var.identity_enabled || var.platform_enabled
    error_message = "The identity cannot be enabled unless the platform is enabled."
  }
}

variable "repository_url" {
  description = "The URL of the Git repository that Argo CD follows. Required when the platform is enabled."
  type        = string
  default     = ""

  validation {
    condition     = !var.platform_enabled || trimspace(var.repository_url) != ""
    error_message = "The repository URL cannot be empty when the platform is enabled."
  }
}

variable "argocd_chart_version" {
  description = "The pinned version of the argo-cd chart. Required when the platform is enabled, and never latest."
  type        = string
  default     = ""

  validation {
    condition     = !var.platform_enabled || (trimspace(var.argocd_chart_version) != "" && lower(trimspace(var.argocd_chart_version)) != "latest")
    error_message = "The argo-cd chart version must be pinned when the platform is enabled: it cannot be empty or latest."
  }
}

variable "argocd_apps_chart_version" {
  description = "The pinned version of the argocd-apps chart. Required when the platform is enabled, and never latest."
  type        = string
  default     = ""

  validation {
    condition     = !var.platform_enabled || (trimspace(var.argocd_apps_chart_version) != "" && lower(trimspace(var.argocd_apps_chart_version)) != "latest")
    error_message = "The argocd-apps chart version must be pinned when the platform is enabled: it cannot be empty or latest."
  }
}

variable "platform_revision" {
  description = "The branch, tag or commit of the repository that the platform Application follows."
  type        = string
  default     = "develop"
}

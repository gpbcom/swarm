variable "machines" {
  description = "The cell machines, each with a unique name, an address and a role (server or agent)."
  type = list(object({
    name    = string
    address = string
    role    = string
  }))

  validation {
    condition     = alltrue([for m in var.machines : contains(["server", "agent"], m.role)])
    error_message = "Each machine role must be server or agent."
  }
}

variable "ssh_user" {
  description = "The user the firewall is configured as over SSH. It needs sudo."
  type        = string
}

variable "ssh_private_key_path" {
  description = "The path of the private key used to connect over SSH."
  type        = string
}

variable "api_allowed_cidrs" {
  description = "The CIDRs, besides the cell machines, allowed to reach the Kubernetes API on 6443/tcp."
  type        = list(string)
  default     = []

  validation {
    condition     = alltrue([for c in var.api_allowed_cidrs : can(cidrnetmask(c))])
    error_message = "Each api_allowed_cidrs entry must be a valid IPv4 CIDR."
  }
}

variable "cluster_cidr" {
  description = "The CIDR of the pods."
  type        = string
  default     = "10.42.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.cluster_cidr))
    error_message = "cluster_cidr must be a valid IPv4 CIDR."
  }
}

variable "service_cidr" {
  description = "The CIDR of the services."
  type        = string
  default     = "10.43.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.service_cidr))
    error_message = "service_cidr must be a valid IPv4 CIDR."
  }
}

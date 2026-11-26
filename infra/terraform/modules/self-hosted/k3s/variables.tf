variable "servers" {
  description = "The control plane machines. The first one initialises the cluster and the others join it."
  type = list(object({
    name    = string
    address = string
  }))

  validation {
    condition     = length(var.servers) > 0
    error_message = "At least one server is required."
  }
}

variable "agents" {
  description = "The worker machines that join the cluster."
  type = list(object({
    name    = string
    address = string
  }))
  default = []
}

variable "ssh_user" {
  description = "The user that Terraform connects as over SSH. It must be able to run sudo without a password."
  type        = string
}

variable "ssh_private_key_path" {
  description = "The path of the private key used to connect over SSH."
  type        = string
}

variable "k3s_version" {
  description = "The pinned k3s release to install, such as v1.31.4+k3s1."
  type        = string

  validation {
    condition     = trimspace(var.k3s_version) != "" && lower(trimspace(var.k3s_version)) != "latest"
    error_message = "The k3s version must be pinned: it cannot be empty or latest."
  }
}

variable "cluster_cidr" {
  description = "The range of addresses given to pods."
  type        = string
  default     = "10.42.0.0/16"
}

variable "service_cidr" {
  description = "The range of addresses given to services."
  type        = string
  default     = "10.43.0.0/16"
}

variable "tls_san" {
  description = "Additional names and addresses the API server certificate must be valid for."
  type        = list(string)
  default     = []
}

variable "kubeconfig_path" {
  description = "Where the kubeconfig is written, outside the repository. The file gets mode 0600."
  type        = string
}

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

  validation {
    condition     = alltrue([for m in var.machines : contains(["server", "agent"], m.role)])
    error_message = "Every machine role must be server or agent."
  }

  validation {
    condition     = length(distinct([for m in var.machines : m.name])) == length(var.machines)
    error_message = "Machine names must be unique."
  }

  validation {
    condition     = length(distinct([for m in var.machines : m.address])) == length(var.machines)
    error_message = "Machine addresses must be unique."
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

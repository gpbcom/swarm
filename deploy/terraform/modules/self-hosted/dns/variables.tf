variable "zone" {
  description = "The DNS zone the records are written to, fully qualified with a trailing dot."
  type        = string

  validation {
    condition     = endswith(var.zone, ".")
    error_message = "The zone must end with a trailing dot."
  }
}

variable "records" {
  description = "The A records to write, as a map of record name to IPv4 address."
  type        = map(string)

  validation {
    condition = alltrue([
      for address in values(var.records) :
      can(regex("^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$", address))
    ])
    error_message = "Every record value must be an IPv4 address."
  }
}

variable "ttl" {
  description = "The time to live of the records, in seconds."
  type        = number
  default     = 300

  validation {
    condition     = var.ttl > 0
    error_message = "The ttl must be positive."
  }
}

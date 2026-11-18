variable "buckets" {
  description = "Names of the buckets to create on the MinIO endpoint."
  type        = set(string)

  validation {
    condition = alltrue([
      for name in var.buckets : can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", name))
    ])
    error_message = "Each bucket name must be 3 to 63 characters of lower-case letters, digits, dots and hyphens, starting and ending with a letter or a digit."
  }
}

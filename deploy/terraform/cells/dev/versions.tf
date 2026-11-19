terraform {
  required_version = ">= 1.10"

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    minio = {
      source  = "aminueza/minio"
      version = "~> 3.0"
    }
    dns = {
      source  = "hashicorp/dns"
      version = "~> 3.4"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 3.0"
    }
  }

  # Partial backend: bucket, key, endpoint, use_path_style, use_lockfile and the rest come from a file kept outside
  # the repository, passed with -backend-config.
  backend "s3" {}
}

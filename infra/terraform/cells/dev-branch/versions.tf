terraform {
  required_version = ">= 1.10"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 3.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Partial backend: bucket, endpoint, use_path_style, use_lockfile and the rest come from a file kept outside the
  # repository, and deploy/scripts/dev-cell.sh passes the key dev-branch/<cell>.tfstate, one state per branch.
  backend "s3" {}
}

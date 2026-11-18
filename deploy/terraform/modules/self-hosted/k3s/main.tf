locals {
  first_server = var.servers[0]
  tls_san_args = join(" ", [for san in var.tls_san : "--tls-san ${san}"])
  install      = "curl -sfL https://get.k3s.io"
  join_url     = "https://${local.first_server.address}:6443"
  ssh_options  = "-i ${var.ssh_private_key_path} -o StrictHostKeyChecking=accept-new -o BatchMode=yes"
}

resource "random_password" "token" {
  length  = 48
  special = false
}

resource "terraform_data" "first_server" {
  triggers_replace = [local.first_server.address, var.k3s_version]

  connection {
    type        = "ssh"
    host        = local.first_server.address
    user        = var.ssh_user
    private_key = file(var.ssh_private_key_path)
  }

  provisioner "remote-exec" {
    inline = [
      "${local.install} | sudo INSTALL_K3S_VERSION='${var.k3s_version}' K3S_TOKEN='${random_password.token.result}' sh -s - server --cluster-init --cluster-cidr ${var.cluster_cidr} --service-cidr ${var.service_cidr} ${local.tls_san_args}",
    ]
  }
}

resource "terraform_data" "server" {
  count = length(var.servers) - 1

  triggers_replace = [var.servers[count.index + 1].address, var.k3s_version]

  connection {
    type        = "ssh"
    host        = var.servers[count.index + 1].address
    user        = var.ssh_user
    private_key = file(var.ssh_private_key_path)
  }

  provisioner "remote-exec" {
    inline = [
      "${local.install} | sudo INSTALL_K3S_VERSION='${var.k3s_version}' K3S_TOKEN='${random_password.token.result}' K3S_URL='${local.join_url}' sh -s - server --cluster-cidr ${var.cluster_cidr} --service-cidr ${var.service_cidr} ${local.tls_san_args}",
    ]
  }

  depends_on = [terraform_data.first_server]
}

resource "terraform_data" "agent" {
  count = length(var.agents)

  triggers_replace = [var.agents[count.index].address, var.k3s_version]

  connection {
    type        = "ssh"
    host        = var.agents[count.index].address
    user        = var.ssh_user
    private_key = file(var.ssh_private_key_path)
  }

  provisioner "remote-exec" {
    inline = [
      "${local.install} | sudo INSTALL_K3S_VERSION='${var.k3s_version}' K3S_TOKEN='${random_password.token.result}' K3S_URL='${local.join_url}' sh -s - agent",
    ]
  }

  depends_on = [terraform_data.first_server]
}

resource "terraform_data" "kubeconfig" {
  triggers_replace = [local.first_server.address, var.kubeconfig_path]

  provisioner "local-exec" {
    command = <<-EOT
      set -eu
      umask 077
      mkdir -p "$(dirname '${var.kubeconfig_path}')"
      ssh ${local.ssh_options} ${var.ssh_user}@${local.first_server.address} sudo cat /etc/rancher/k3s/k3s.yaml \
        | sed 's#127.0.0.1#${local.first_server.address}#' > '${var.kubeconfig_path}'
      chmod 0600 '${var.kubeconfig_path}'
    EOT
  }

  depends_on = [terraform_data.first_server]
}

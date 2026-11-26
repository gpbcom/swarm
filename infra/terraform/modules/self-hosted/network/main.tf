locals {
  machine_addresses = [for m in var.machines : m.address]
  server_addresses  = [for m in var.machines : m.address if m.role == "server"]
  api_sources       = distinct(concat(local.machine_addresses, var.api_allowed_cidrs))

  commands = concat(
    [
      "sudo ufw --force reset",
      "sudo ufw default deny incoming",
      "sudo ufw default allow outgoing",
      "sudo ufw allow 22/tcp",
    ],
    [for s in local.api_sources : "sudo ufw allow from ${s} to any port 6443 proto tcp"],
    [for s in local.machine_addresses : "sudo ufw allow from ${s} to any port 10250 proto tcp"],
    [for s in local.machine_addresses : "sudo ufw allow from ${s} to any port 8472 proto udp"],
    [for s in local.server_addresses : "sudo ufw allow from ${s} to any port 2379:2380 proto tcp"],
    [
      "sudo ufw allow from ${var.cluster_cidr}",
      "sudo ufw allow from ${var.service_cidr}",
      "sudo ufw --force enable",
    ],
  )
}

resource "terraform_data" "firewall" {
  for_each = { for m in var.machines : m.name => m }

  triggers_replace = {
    address  = each.value.address
    commands = local.commands
  }

  connection {
    type        = "ssh"
    host        = each.value.address
    user        = var.ssh_user
    private_key = file(var.ssh_private_key_path)
  }

  provisioner "remote-exec" {
    inline = local.commands
  }
}

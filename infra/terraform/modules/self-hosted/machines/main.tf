resource "terraform_data" "machine" {
  for_each = { for m in var.machines : m.name => m }

  triggers_replace = each.value.address

  connection {
    type        = "ssh"
    host        = each.value.address
    user        = var.ssh_user
    private_key = file(var.ssh_private_key_path)
  }

  provisioner "remote-exec" {
    inline = [
      "sudo hostnamectl set-hostname ${each.value.name}",
      "sudo apt-get update",
      "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y curl ca-certificates",
    ]
  }
}

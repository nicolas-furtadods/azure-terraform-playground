module "templates" {
  source = "git::https://github.com/nicolas-furtadods/azure-terraform-playground.git//modules/virtual_network?ref=fastapi"
  for_each = {
    for k, subnet in var.subnets : k => subnet if var.template_folder != null && var.template_folder != "" && subnet.template != null && subnet.template != ""
  }
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.nsg[each.key].name
  rules_file                  = lookup(local.template_map, each.value.template)
}

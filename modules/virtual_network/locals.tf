locals {
  naming = replace(lower("${var.application}-${var.environment}"), " ", "")

  local_tags = {
    application = var.application
    environment = var.environment
    location    = var.location
    managed_by  = "Terraform"
  }

  tags = merge(var.tags, local.local_tags)

  reserved_subnets = [
    "GatewaySubnet",
    "AzureBastionSubnet",
    "AzureFirewallSubnet",
    "AzureFirewallManagementSubnet",
    "RouteServerSubnet"
  ]

  #Resource Group Name
  resource_group_name = var.resource_group_name == null ? azurerm_resource_group.this[0].name : var.resource_group_name

  nsg_files = fileset(var.template_folder, "*.json")
  template_map = {
    for k, f in local.nsg_files : replace(k, ".json", "") => file("${var.template_folder}/${f}")
  }
}
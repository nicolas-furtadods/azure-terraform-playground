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
  resource_group_name = var.resource_group_name == null ? azurerm_resource_group.name : var.resource_group_name
}
resource "azurerm_resource_group" "this" {
  count = var.resource_group_name == null ? 1 : 0
  
  name = "${local.naming}-rg"
  location = var.location
  tags = local.tags
}


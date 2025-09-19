resource "azurerm_virtual_network" "this" {
  name                = "${local.naming}-vnet"
  address_space       = var.vnet_cidr_block
  resource_group_name = local.resource_group_name
  location            = var.location
  tags                = var.tags
}

resource "azurerm_virtual_network_dns_servers" "dns" {
  count              = length(var.vnet_dns_server) > 0 ? 1 : 0
  virtual_network_id = azurerm_virtual_network.this.id
  dns_servers        = var.vnet_dns_server
}
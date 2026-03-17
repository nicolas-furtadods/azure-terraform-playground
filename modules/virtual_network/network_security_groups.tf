resource "azurerm_network_security_group" "these" {
  for_each            = var.subnets
  name                = "snet-${local.naming}-${each.value.shortname}-nsg"
  resource_group_name = local.resource_group_name
  location            = var.location
  tags                = local.tags
}

resource "azurerm_subnet_network_security_group_association" "subnets_to_nsg" {
  depends_on                = [module.templates]
  for_each                  = var.subnets
  subnet_id                 = azurerm_subnet.these[each.key].id
  network_security_group_id = azurerm_network_security_group.these[each.key].id

}
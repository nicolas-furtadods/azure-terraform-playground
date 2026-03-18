resource "azurerm_route_table" "these" {
  for_each            = var.subnets
  name                = "snet-${local.naming}-${each.value.shortname}-rtb"
  location            = var.location
  resource_group_name = local.resource_group_name
  tags                = local.tags
}

resource "azurerm_subnet_route_table_association" "subnets_to_routes" {
  for_each       = {
    for key, value in var.subnets : key => value if value.enforce_route_table_association == true
  }
  subnet_id      = azurerm_subnet.these[each.key].id
  route_table_id = azurerm_route_table.these[each.key].id

}
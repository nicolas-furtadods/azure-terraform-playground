resource "azurerm_public_ip" "t" {
  count               = var.enable_nat_gateway ? 1 : 0
  name                = "${local.naming}-pip"
  resource_group_name = local.resource_group_name
  location            = var.location
  tags                = local.tags
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_nat_gateway" "this" {
  count                   = var.enable_nat_gateway ? 1 : 0
  name                    = "${local.naming}-nat"
  resource_group_name     = local.resource_group_name
  location                = var.location
  tags                    = local.tags
  sku_name     = "Standard"
  idle_timeout_in_minutes = 10
}

resource "azurerm_nat_gateway_public_ip_association" "ip_to_nat" {
  count                = var.enable_nat_gateway ? 1 : 0
  nat_gateway_id       = azurerm_nat_gateway.this[0].id
  public_ip_address_id = azurerm_public_ip.nat_ip[0].id
}

resource "azurerm_subnet_nat_gateway_association" "subnets_to_nat" {
  for_each = {
    for k, subnet in azurerm_subnet.subnet :
    k => subnet if azurerm_subnet.subnet[k].name != "gateway_subnet" && var.enable_nat_gateway
  }
  subnet_id      = azurerm_subnet.these[each.key].id
  nat_gateway_id = azurerm_nat_gateway.this[0].id
}
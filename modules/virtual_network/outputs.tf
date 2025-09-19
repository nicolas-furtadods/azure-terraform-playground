output "virtual_network" {
  value = {
    id   = azurerm_virtual_network.this.id
    name = azurerm_virtual_network.this.name
    subnets = {
      for k, subnet in var.subnets : k => {
        subnet_id : azurerm_subnet.subnet[k].id
        address_prefix : azurerm_subnet.subnet[k].address_prefixes
        network_security_group_id : azurerm_network_security_group.these[k].id
        network_security_group_name : azurerm_network_security_group.these[k].name
        route_table_id : azurerm_route_table.these[k].id
        route_table_name : azurerm_route_table.these[k].name
      }
    }
  }
}
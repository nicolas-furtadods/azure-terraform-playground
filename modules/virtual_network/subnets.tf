resource "azurerm_subnet" "these" {
  depends_on = [
    azurerm_virtual_network.vnet
  ]
  for_each                                      = var.subnets
  name                                          = contains(local.reserved_subnets, each.value.shortname) ? each.value.shortname : "snet-${var.environment}-${each.value.shortname}"
  resource_group_name                           = local.resource_group_name
  virtual_network_name                          = azurerm_virtual_network.this.name
  address_prefixes                              = tolist([each.value.cidr])
  service_endpoints                             = each.value.service_endpoints
  dynamic "delegation" {
    for_each = each.value.delegation
    iterator = delegation
    content {
      name = delegation.value.name
      dynamic "service_delegation" {
        for_each = delegation.value.service_delegation
        iterator = service_delegation
        content {
          name    = service_delegation.value.name    # (Required) The name of service to delegate to. Possible values include Microsoft.BareMetal/AzureVMware, Microsoft.BareMetal/CrayServers, Microsoft.Batch/batchAccounts, Microsoft.ContainerInstance/containerGroups, Microsoft.Databricks/workspaces, Microsoft.HardwareSecurityModules/dedicatedHSMs, Microsoft.Logic/integrationServiceEnvironments, Microsoft.Netapp/volumes, Microsoft.ServiceFabricMesh/networks, Microsoft.Sql/managedInstances, Microsoft.Sql/servers, Microsoft.Web/hostingEnvironments and Microsoft.Web/serverFarms.
          actions = service_delegation.value.actions # (Required) A list of Actions which should be delegated. Possible values include Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action, Microsoft.Network/virtualNetworks/subnets/action and Microsoft.Network/virtualNetworks/subnets/join/action.
        }
      }
    }
  }

}

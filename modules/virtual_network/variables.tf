
variable "application" {
  description = "Name of the application for which the virtual network is created (agw,corenet etc.)"
  type        = string
  default     = "defaultVnet"
}

variable "environment" {
  description = "Enter the 3-digits environment which will be used by resources (hpr,sbx,prd,hyb)"
  type        = string
  default     = "dev"
  validation {
    condition = (
      length(var.environment) > 0 && length(var.environment) <= 3
    )
    error_message = "The environment must be a 3-digits string."
  }
}

variable "location" {
  description = "Enter the region for which to create the resources."
  default     = "francecentral"
}

variable "tags" {
  description = "Tags to apply to your resources"
  type        = map(string)
  default     = {}
}

variable "resource_group_name" {
  description = "(Optionnal)Name of the resource group where resources will be created"
  type        = string
  default     = null
}

variable "vnet_cidr_block" {
  description = "CIDR block for VNET"
  type        = list(string)
}

variable "vnet_dns_server" {
  description = "VNET DNS server if you wish to use your custom DNS"
  type        = list(string)
  default     = []
}

variable "enable_nat_gateway" {
  description = "Enale the creation and assignment of a NAT Gateway ?"
  type        = bool
  default     = false
}

variable "subnets" {
  description = "Map of resources and security rules"
  type = map(object({
    shortname                                     = string
    cidr                                          = string
    private_link_service_network_policies_enabled = bool
    private_endpoint_network_policies_enabled     = bool
    service_endpoints                             = list(string)
    template                                      = string
    delegation = list(object({
      name = string
      service_delegation = list(object({
        name    = string       # (Required) The name of service to delegate to. Possible values include Microsoft.BareMetal/AzureVMware, Microsoft.BareMetal/CrayServers, Microsoft.Batch/batchAccounts, Microsoft.ContainerInstance/containerGroups, Microsoft.Databricks/workspaces, Microsoft.HardwareSecurityModules/dedicatedHSMs, Microsoft.Logic/integrationServiceEnvironments, Microsoft.Netapp/volumes, Microsoft.ServiceFabricMesh/networks, Microsoft.Sql/managedInstances, Microsoft.Sql/servers, Microsoft.Web/hostingEnvironments and Microsoft.Web/serverFarms.
        actions = list(string) # (Required) A list of Actions which should be delegated. Possible values include Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action, Microsoft.Network/virtualNetworks/subnets/action and Microsoft.Network/virtualNetworks/subnets/join/action.
      }))
    }))
  }))
}


variable "diagnostic_settings" {
  description = "Object structure for information regarding diagnostics settings"
  type = object({
    network_watcher = object({
      network_watcher_name                = string
      network_watcher_resource_group_name = string
    })
    log_analytics = object({
      workspace_id          = string
      workspace_resource_id = string
      workspace_region      = string
      interval_in_minutes   = number
    })
    storage_account = object({
      storage_account_id = string
      retention_days     = number
    })
  })
  default = null
}
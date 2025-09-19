variable "rules_file" {
  description = "A file set of Security rules for a specific network security group."
  type        = string
  default     = "[]"
}

variable "network_security_group_name" {
  type        = string
  description = "Network Security Group Name to apply the security rules files."
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}
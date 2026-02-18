variable "compartment_ocid" {
  description = "OCID from your tenancy page"
  type        = string
}

variable "root_compartment_ocid" {
  description = "OCID tenancy"
  type = string
}

variable "oci_region" {
  description = "region where you have OCI tenancy"
  type        = string
  default     = "us-ashburn-1"
}

variable "compartment_name" {
  type = string
}

variable "oci_region_backup" {
  type = string
}

variable "environment" {
  type = string
}

variable "product" {
  type = string
}

variable "team" {
  type = string
}

variable "user" {
  type = string
}
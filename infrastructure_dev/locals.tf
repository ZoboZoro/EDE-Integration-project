locals {
    Project_Name = "ede_multisource_project"
    Managed_by   = "terrfaorm"
    Environment  = "production"
}

locals {
  common_tags = {
    Project_Name = "ede_multisource_project"
    Managed_by   = "terrfaorm"
    Owner = "Taofeecoh"
    Github = "github.com/zobozoro"
    Environment  = "production"
  }
}
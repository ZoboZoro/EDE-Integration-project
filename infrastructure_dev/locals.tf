locals {
    project_name = "ede_multisource_project"
    managed_by   = "terrfaorm"
    environment  = "development"
}

locals {
  common_tags = {
    project_name = "ede_multisource_project"
    managed_by   = "terrfaorm"
    owner = "Taofeecoh"
    github = "github.com/zobozoro"
    environment  = "development"
  }
}
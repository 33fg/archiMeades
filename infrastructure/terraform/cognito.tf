# WO-9: AWS Cognito User Pool and Configuration
# MFA, password policy, role-based groups (researcher, admin, viewer)

resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-user-pool"

  # Password policy
  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                 = true
    temporary_password_validity_days = 7
  }

  # MFA configuration
  mfa_configuration = "OPTIONAL" # Set to "ON" to require MFA

  # User attributes
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }
  schema {
    name                = "name"
    attribute_data_type = "String"
    required            = false
    mutable             = true
  }

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Token expiration
  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  # Advanced security (optional)
  user_pool_add_ons {
    advanced_security_mode = "AUDIT"
  }

  tags = {
    Name = "${var.project_name}-user-pool"
  }
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project_name}-${var.cognito_domain_suffix}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# User groups for role-based access
resource "aws_cognito_user_group" "researcher" {
  name         = "researcher"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Researcher role - full access to simulations and theories"
  precedence   = 10
}

resource "aws_cognito_user_group" "admin" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Admin role - full platform access"
  precedence   = 5
}

resource "aws_cognito_user_group" "viewer" {
  name         = "viewer"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Viewer role - read-only access"
  precedence   = 20
}

# App client for React frontend
resource "aws_cognito_user_pool_client" "web" {
  name         = "${var.project_name}-web-client"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret                      = false
  explicit_auth_flows                  = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"]
  prevent_user_existence_errors        = "ENABLED"
  access_token_validity                = 1   # hours
  id_token_validity                    = 1   # hours
  refresh_token_validity               = 30  # days
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  read_attributes  = ["email", "name", "email_verified"]
  write_attributes = ["email", "name"]
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "ecs_api_cluster_name" {
  value = aws_ecs_cluster.api.name
}

output "ecs_workers_cluster_name" {
  value = aws_ecs_cluster.workers.name
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "alb_target_group_arn" {
  value = aws_lb_target_group.api.arn
}

# Cognito outputs (WO-9)
output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  value     = aws_cognito_user_pool_client.web.id
  sensitive = true
}

output "cognito_jwks_url" {
  value = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main.id}/.well-known/jwks.json"
}

output "cognito_domain" {
  value = aws_cognito_user_pool_domain.main.domain
}

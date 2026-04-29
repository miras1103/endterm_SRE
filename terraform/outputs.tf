output "public_ip_address" {
  description = "Public IP address of the provisioned EC2 instance"
  value       = aws_instance.application_server.public_ip
}

output "frontend_url" {
  description = "Frontend URL"
  value       = "http://${aws_instance.application_server.public_ip}"
}

output "grafana_url" {
  description = "Grafana URL"
  value       = "http://${aws_instance.application_server.public_ip}:3000"
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = "http://${aws_instance.application_server.public_ip}:9090"
}

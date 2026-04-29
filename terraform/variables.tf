variable "project_name" {
  description = "Project name used for AWS resource tags"
  type        = string
  default     = "microservices-incident-response"
}

variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
}

variable "availability_zone" {
  description = "Availability zone for the public subnet"
  type        = string
}

variable "instance_ami" {
  description = "Amazon Machine Image ID for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "key_pair_name" {
  description = "Existing AWS key pair name for SSH access"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to access SSH"
  type        = string
  default     = "0.0.0.0/0"
}

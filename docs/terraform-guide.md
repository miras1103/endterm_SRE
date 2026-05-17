# Terraform Infrastructure Documentation

Student: Miras Aliyev  
Group: SE-2427  
Project: Reliability Hub

## Purpose

This document explains the Infrastructure as Code part of the project. Terraform is used to provision AWS infrastructure in a repeatable and automated way.

## Terraform Files

The Terraform configuration is stored in the `terraform` folder.

| File               | Purpose                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `main.tf`          | Creates the AWS provider configuration, VPC, subnet, internet gateway, route table, security group, and EC2 instance. |
| `variables.tf`     | Defines configurable values such as AWS region, AMI, instance type, key pair name, and SSH CIDR.                      |
| `terraform.tfvars` | Provides actual values for the variables.                                                                             |
| `outputs.tf`       | Prints the public IP address and service URLs after infrastructure creation.                                          |

## Provisioned Infrastructure

Terraform creates the following AWS resources:

1. VPC
2. Public subnet
3. Internet gateway
4. Public route table
5. Route table association
6. Security group
7. EC2 virtual machine

## Network Access Rules

The security group allows the required ports:

| Port   | Service    | Purpose                            |
| ------ | ---------- | ---------------------------------- |
| `22`   | SSH        | Remote access to the Ubuntu server |
| `80`   | HTTP       | Frontend access                    |
| `3000` | Grafana    | Monitoring dashboard               |
| `9090` | Prometheus | Metrics and targets                |

## Required Tools

Install these tools before running Terraform:

1. Terraform
2. AWS CLI
3. AWS account
4. AWS access key and secret access key
5. AWS EC2 key pair

## AWS CLI Configuration

Run this command on Windows PowerShell:

```powershell
aws configure
```

Enter:

```text
AWS Access Key ID
AWS Secret Access Key
Default region name: us-east-1
Default output format: json
```

## Variable Configuration

Edit `terraform/terraform.tfvars`.

Example:

```hcl
aws_region        = "us-east-1"
availability_zone = "us-east-1a"
instance_ami      = "ami-0c7217cdde317cfec"
instance_type     = "t3.micro"
key_pair_name     = "miras-key"
allowed_ssh_cidr  = "0.0.0.0/0"
```

`key_pair_name` must match the name of an existing key pair in AWS EC2.

## Terraform Commands

Open PowerShell in the project folder.

```powershell
cd terraform
```

Initialize Terraform:

```powershell
terraform init
```

Preview infrastructure changes:

```powershell
terraform plan
```

Create infrastructure:

```powershell
terraform apply
```

Type:

```text
yes
```

Show output values:

```powershell
terraform output
```

## Expected Outputs

Terraform prints:

```text
public_ip_address
frontend_url
grafana_url
prometheus_url
```

Example:

```text
frontend_url   = "http://PUBLIC_IP"
grafana_url    = "http://PUBLIC_IP:3000"
prometheus_url = "http://PUBLIC_IP:9090"
```

## Deploy Application On Ubuntu EC2

Connect to the server:

```powershell
ssh -i miras-key.pem ubuntu@PUBLIC_IP
```

Install Docker:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

Exit and connect again:

```bash
exit
```

Copy the project from Windows to EC2:

```powershell
scp -i miras-key.pem -r <project-directory> ubuntu@PUBLIC_IP:/home/ubuntu/endterm
```

Run the project on Ubuntu:

```bash
cd /home/ubuntu/endterm
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml up --build -d
docker compose ps
```

Open in browser:

```text
http://PUBLIC_IP
http://PUBLIC_IP:3000
http://PUBLIC_IP:9090
```

## Evidence To Include

For the endterm report, include these screenshots:

1. `terraform init` success
2. `terraform plan` output
3. `terraform apply` success
4. `terraform output`
5. AWS EC2 instance running
6. AWS Security Group inbound rules
7. SSH connection to Ubuntu server
8. `docker compose ps` on Ubuntu
9. Frontend opened by public IP
10. Grafana opened by public IP and port `3000`
11. Prometheus opened by public IP and port `9090`

## Common Errors

### Instance Type Is Not Free Tier Eligible

Error:

```text
InvalidParameterCombination: The specified instance type is not eligible for Free Tier
```

Fix:

```hcl
instance_type = "t3.micro"
```

Then run:

```powershell
terraform plan
terraform apply
```

### Key Pair Not Found

Error:

```text
InvalidKeyPair.NotFound
```

Fix:

Make sure `key_pair_name` in `terraform.tfvars` exactly matches the AWS EC2 key pair name.

### Website Does Not Open

Check:

1. EC2 instance is running
2. Security group allows port `80`
3. Docker containers are running
4. Frontend container is mapped to port `80`

Command:

```bash
docker compose ps
```

## Destroy Infrastructure

After finishing evidence capture or defense, destroy the infrastructure to avoid AWS charges:

```powershell
terraform destroy
```

Type:

```text
yes
```

## Defense Explanation

Use this explanation during defense:

```text
For the endterm project, I used Terraform to provision AWS infrastructure. The configuration creates a VPC, public subnet, internet gateway, route table, security group, and EC2 instance. The security group opens SSH, HTTP, Grafana, and Prometheus ports. Terraform outputs the public IP address and service URLs. This makes the infrastructure reproducible because the same environment can be created again using terraform init, terraform plan, and terraform apply.
```

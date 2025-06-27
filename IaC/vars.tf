variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ec2_ami" {
  type    = string
  default = "ami-034568121cfdea9c3" // double check to make sure this is the most recent Ubuntu 22.04 LTS AMI for your AWS Region
}

variable "public_subnet_cidrs" {
 type        = list(string)
 description = "Public Subnet CIDR values"
 default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}
 
variable "private_subnet_cidrs" {
 type        = list(string)
 description = "Private Subnet CIDR values"
 default     = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
}
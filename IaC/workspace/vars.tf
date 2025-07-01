variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ubuntu_image_id" {
  type = string
  default = "ami-020cba7c55df1f615" # This is an example AMI ID for Ubuntu 20.04 in us-east-1; update as needed.
  validation {
    condition     = can(regex("^ami-[a-z0-9]+$", var.ubuntu_image_id))
    error_message = "The Ubuntu image ID must be in the format ami-xxxxxxxxxxxx."
  }
  description = "The ID of the Ubuntu image to use."
}

variable "ec2_key_name_putty" {
  type        = string
  description = "Name of the EC2 key pair for SSH access via putty"
  default     = "audio-curl-bot-putty"
}

variable "ec2_key_name_key" {
  type        = string
  description = "Name of the EC2 key pair for SSH access via key pair"
  default     = "audio-curl-bot-key"
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
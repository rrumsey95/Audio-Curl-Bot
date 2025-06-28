// allow http and https traffic to the bot networking security group
resource "aws_security_group" "bot_networking" {
  name        = "bot_networking"
  description = "Allow HTTP and HTTPS inbound traffic and all outbound traffic"
  vpc_id      = aws_vpc.audio-curl-bot-vpc.id

  tags = {
    Name = "bot_networking"
  }
}

resource "aws_vpc_security_group_ingress_rule" "bot_networking_http_ipv4" {
  security_group_id = aws_security_group.bot_networking.id
  cidr_ipv4         = aws_vpc.audio-curl-bot-vpc.cidr_block
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}
/*
resource "aws_vpc_security_group_ingress_rule" "bot_networking_http_ipv6" {
  security_group_id = aws_security_group.bot_networking.id
  cidr_ipv6         = aws_vpc.audio-curl-bot-vpc.ipv6_cidr_block
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}
*/
resource "aws_vpc_security_group_ingress_rule" "bot_networking_https_ipv4" {
  security_group_id = aws_security_group.bot_networking.id
  cidr_ipv4         = aws_vpc.audio-curl-bot-vpc.cidr_block
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}
/*
resource "aws_vpc_security_group_ingress_rule" "bot_networking_https_ipv6" {
  security_group_id = aws_security_group.bot_networking.id
  cidr_ipv6         = aws_vpc.audio-curl-bot-vpc.ipv6_cidr_block
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}
*/
resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.bot_networking.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}
/*
resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv6" {
  security_group_id = aws_security_group.bot_networking.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}
*/
// allow ssh traffic to the bot networking security group
// This security group is used to allow SSH access to the bot instances for management purposes.
resource "aws_security_group" "bot_ssh_networking" {
  name        = "bot_ssh_networking"
  description = "Allow ssh traffic"
  vpc_id      = aws_vpc.audio-curl-bot-vpc.id

  tags = {
    Name = "bot_ssh_networking"
  }
}

resource "aws_vpc_security_group_ingress_rule" "bot_ssh_networking_ipv4" {
  security_group_id = aws_security_group.bot_ssh_networking.id
  cidr_ipv4         = aws_vpc.audio-curl-bot-vpc.cidr_block
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}
/*
resource "aws_vpc_security_group_ingress_rule" "bot_ssh_networking_ipv6" {
  security_group_id = aws_security_group.bot_ssh_networking.id
  cidr_ipv6         = aws_vpc.audio-curl-bot-vpc.ipv6_cidr_block
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}
*/
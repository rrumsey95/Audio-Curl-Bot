resource "aws_instance" "audio-curl-bot-ec2" {
  ami = var.ubuntu_image_id
  instance_type = "t2.micro"
  user_data = templatefile("audio-curl-bot-ec2-user-data.sh", {
    env_file     = data.aws_secretsmanager_secret_version.env_file.secret_string
    cookies_file = data.aws_secretsmanager_secret_version.cookies_file.secret_string
  })
  subnet_id = aws_subnet.public_subnets[0].id
  vpc_security_group_ids = [aws_security_group.bot_networking.id, aws_security_group.bot_ssh_networking.id]
  key_name = var.ec2_key_name_putty
  user_data_replace_on_change = true
  // associate_public_ip_address = true
  // iam_instance_profile = aws_iam_instance_profile.audio-curl-bot-ec2-profile.name // not yet implemented

  tags = {
    Name = "audio-curl-bot-ec2"
    env = "prod"
    project = "audio-curl-bot"
  }
}

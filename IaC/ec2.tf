resource "aws_instance" "audio-curl-bot-ec2" {
  ami = var.ec2_ami
  instance_type = "t2.micro"
  user_data = file("audio-curl-bot-ec2-user-data.sh")
  subnet_id = aws_subnet.audio-curl-bot-subnet.id
  vpc_security_group_ids = [aws_security_group.bot_networking.id, aws_security_group.bot_ssh_networking.id]
  key_name = var.ec2_key_name_putty

  tags = {
    Name = "audio-curl-bot-ec2"
    env = "prod"
  }
}

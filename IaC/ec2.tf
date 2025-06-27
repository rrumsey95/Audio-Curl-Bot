/*
resource "aws_instance" "audio-curl-bot-ec2" {
  ami = var.ec2_ami
  instance_type = "t2.micro"
  user_data = file("audio-curl-bot-ec2-user-data.sh")
  // subnet_id = "subnet-0065cc1c08538f592"

  tags = {
    Name = "audio-curl-bot-ec2"
    env = "prod"
  }
}
*/
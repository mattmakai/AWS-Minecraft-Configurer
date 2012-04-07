import boto, os, time


def create_key_pair(name, location):
  """ location example: '/home/matt/.ssh' """
  ec2 = boto.connect_ec2()
  key_pair = ec2.create_key_pair(name)
  key_pair.save(location)


def connect_ec2():
  return boto.connect_ec2()


def launch_instance(ec2, key_pair_name, security_group_name='mcserver',
    ssh_port=22, cidr='0.0.0.0/0'):

  try:
    group = ec2.get_all_security_groups(groupnames=[security_group_name])[0]
  except ec2.ResponseError, e:
    if e.code == 'InvalidGroup.NotFound':
      group = ec2.create_security_group(security_group_name, 
        'Minecraft security group.')
      group.authorize('tcp', ssh_port, ssh_port, cidr)
    else:
      raise

  reservation = ec2.run_instances(image_id='ami-3e9b4957',
    instance_type='t1.micro', user_data=None, key_name=key_pair_name,
    security_groups=[group])
  instance = reservation.instances[0]
  return instance


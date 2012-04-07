import boto, os, time


def create_key_pair(name):
  ec2 = boto.connect_ec2()
  key_pair = ec2.create_key_pair(name)
  key_pair.save('/home/matt/.ssh')


def connect_ec2():
  return boto.connect_ec2()


def launch_instance(ec2, key_pair_name, security_group_name='makaidjango',
    ssh_port=22, cidr='0.0.0.0/0'):

  try:
    group = ec2.get_all_security_groups(groupnames=[security_group_name])[0]
  except ec2.ResponseError, e:
    if e.code == 'InvalidGroup.NotFound':
      group = ec2.create_security_group(security_group_name, 
        'Django security group.')
      group.authorize('tcp', ssh_port, ssh_port, cidr)
    else:
      raise

  reservation = ec2.run_instances(image_id='ami-3e9b4957',
    instance_type='t1.micro', user_data=None, key_name=key_pair_name,
    security_groups=[group])
  instance = reservation.instances[0]
  return instance


def bucket_byte_size(bucket_name):
  s3 = boto.connect_s3()
  total_bytes = 0
  bucket = s3.lookup(bucket_name)
  if bucket:
    for key in bucket:
      total_bytes += key.size
  else:
    print 'Warning: bucket %s was not found!' % bucket_name
  return total_bytes


def upload_to_s3(bucket_name, website_dir, index_file, error_file=None):
  """This code is by Mitch Garnaat in Python & AWS Cookbook - an
  amazing reference for boto and AWS!"""
  s3 = boto.connect_s3()
  bucket = s3.lookup(bucket_name)
  bucket.set_canned_acl('public-read')
  for root, dirs, files in os.walk(website_dir):
    for file in files:
      full_path = os.path.join(root, file)
      rel_path = os.path.relpath(full_path, website_dir)
      print 'Uploading %s as %s' % (full_path, rel_path)
      key = bucket.new_key(rel_path)
      key.content_type = 'text/html'
      key.set_contents_from_filename(full_path, policy='public-read')
  bucket.configure_website(index_file, error_file)

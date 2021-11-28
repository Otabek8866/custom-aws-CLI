import boto3
import os
from botocore.exceptions import ClientError


# Create a security group
def create_sec_group(ec2, security_group_name):

    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try:
        response = ec2.create_security_group(GroupName=security_group_name,
                                             Description='DESCRIPTION',
                                             VpcId=vpc_id)

        security_group_id = response['GroupId']
        print('Security Group Created id: %s in vpc id: %s.' % (security_group_id, vpc_id))

        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])

    except ClientError as e:
        print(e)


# Create a KeyPair and write key in a file
def create_key_pair(ec2_client, key_name):
    key_pair = ec2_client.create_key_pair(KeyName=key_name)
    private_key = key_pair["KeyMaterial"]

    # write private key to file with 400 permissions
    with os.fdopen(os.open(key_name+".pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)


# Create an instance
def create_instance(ec2_client, imageID, mincount, maxcount, instancetype, keyname, security_group_id):
    instances = ec2_client.run_instances(
        ImageId=imageID,
        MinCount=mincount,
        MaxCount=maxcount,
        InstanceType=instancetype,
        KeyName=keyname,
        Monitoring={'Enabled': True},
        SecurityGroupIds=[security_group_id,]

    )

    print("Instance created with the following ID:")
    print(instances["Instances"][0]["InstanceId"])

    return instances["Instances"][0]["InstanceId"]


# list all the instances running in one region
def get_running_instances(ec2_resource):
    i = 1
    for item in ec2_resource.instances.all():
        print(i, "- ID:", item.id, "State:", item.state["Name"], "Public IP:", item.public_ip_address)
        i = i + 1


# Listing all the available regions
def list_regions(ec2_client):
    response = ec2_client.describe_regions()

    print("Available regions and endpoints:")
    for resp in response['Regions']:
        print("-" * 40)
        region_name = resp['RegionName']
        end_point = resp['Endpoint']
        print("Region name:", region_name)
        print("Endpoint:", end_point)
    
    print("-" * 40)


#Stopping an instance
def start_stop_instance(ec2_client, instance_id, status=True):
    if status:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
    else:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])


# Terminating an instance
def terminate_instance(ec2_client, instance_id):
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    

# Status of an instance
def status_instance(ec2_resource, id_instance):
    instance = ec2_resource.Instance(id_instance)
    print("ID:"+str(instance.id), "   State:"+str(instance.state["Name"]), "   Public IP:"+str(instance.public_ip_address))

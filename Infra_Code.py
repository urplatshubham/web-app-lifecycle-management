import boto3

def create_s3_bucket(): #creating a s3 bucket
    s3 = boto3.client('s3')
    bucket_name = 'ShubhamR-webapp-bucket'

    response = s3.create_bucket(Bucket=bucket_name)
    print(f'S3 bucket {bucket_name} created successfully.') #successful creation of S3 

def launch_ec2(): #creating a ec2 instance
    ec2 = boto3.resource('ec2')  
    instances = ec2.create_instances(
            ImageId='ami-05134c8ef96964280',  # Copied from existing EC2 instances leveraging latest AMI ID of the region
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='Shubham-instance',#my existing key-pair in AWS consolde
            SecurityGroupIds=['sg-0ff7dc4e0c607385a'],

            #this is for the configuration of the ngnix server setup for reverse proxy 
            UserData='''#!/bin/bash
            sudo apt update
            sudo apt install -y nginx
            sudo systemctl start nginx
            sudo systemctl enable nginx
            '''
            TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'MyWebServer'  # Give your EC2 instance a name here
                    }
                ]
            }
        ]
    )
    instance_id = instances[0].id
    print(f'EC2 instance {instance_id} launched successfully.') 
    return instance_id

def create_load_balancer(instance_id): #load balancer creation
    elb = boto3.client('elbv2')
     
    response = elb.create_load_balancer(
        Name='ShubhamR-load-balancer',
        Subnets=['subnet-0f30c30418def6379', 'subnet-09bd0e0acc92d4efa'],  # 2 different subnets from 2 different availability zone
        SecurityGroups=['sg-123abc']
    )

    lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    print(f'Load balancer created with ARN: {lb_arn}')

    target_group = elb.create_target_group(
        Name='ShubhamR-target-group',
        Protocol='HTTP',
        Port=80,
        VpcId='vpc-0321f38a7b594180d'
    )

    tg_arn = target_group['TargetGroups'][0]['TargetGroupArn']

    elb.register_targets(
        TargetGroupArn=tg_arn,
        Targets=[{'Id': instance_id}]
    )
    print(f'EC2 instance {instance_id} registered with target group {tg_arn}.')
    return lb_arn, tg_arn

def configure_asg(instance_id, tg_arn):
    autoscaling = boto3.client('autoscaling')

    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='ShubhamR-asg',
        InstanceId=instance_id,
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=1,
        TargetGroupARNs=[tg_arn],
        VPCZoneIdentifier='subnet-0f30c30418def6379,subnet-09bd0e0acc92d4efa'
    )
    print(f'Auto Scaling Group created and linked to target group.')

    cloudwatch = boto3.client('cloudwatch')

    scaling_policy = autoscaling.put_scaling_policy(
        AutoScalingGroupName='ShubhamR-asg',
        PolicyName='scale-out-policy',
        AdjustmentType='ChangeInCapacity',
        ScalingAdjustment=1,
        Cooldown=300
    )
    print(f'Scaling policy for scale-out configured.')

def setup_sns():
    sns = boto3.client('sns')

    topic = sns.create_topic(Name='infra-alerts')
    topic_arn = topic['TopicArn']

    # Subscribe admin email to the topic
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint='admin@example.com'
    )
    print(f'SNS Topic {topic_arn} created and subscription added.')
    return topic_arn

def deploy_infrastructure():
    create_s3_bucket()
    instance_id = launch_ec2()
    lb_arn, tg_arn = create_load_balancer(instance_id)
    configure_asg(instance_id, tg_arn)
    sns_topic_arn = setup_sns()
    return lb_arn, tg_arn, [instance_id], sns_topic_arn

def delete_auto_scaling_group(asg_name):
    autoscaling = boto3.client('autoscaling')
    
    # Delete Auto Scaling Group
    autoscaling.delete_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        ForceDelete=True
    )
    print(f"Auto Scaling Group {asg_name} deleted.")

def delete_load_balancer(lb_arn, tg_arn):
    elb = boto3.client('elbv2')
    
    # Deleting the Load Balancer
    elb.delete_load_balancer(LoadBalancerArn=lb_arn)
    print(f"Load Balancer {lb_arn} deleted.")
    
    # Deleting the Target Group
    elb.delete_target_group(TargetGroupArn=tg_arn)
    print(f"Target Group {tg_arn} deleted.")

def terminate_ec2_instances(instance_ids):
    ec2 = boto3.client('ec2')
    
    # Terminating EC2 instance which have been passed to this function only
    ec2.terminate_instances(InstanceIds=instance_ids)
    print(f"EC2 instances {instance_ids} terminated.")
    
    # Waiting until instances are terminated
    ec2.get_waiter('instance_terminated').wait(InstanceIds=instance_ids)
    print(f"EC2 instances {instance_ids} terminated and cleaned up.")

def empty_and_delete_s3_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    # Deleting all objects in the bucket
    bucket.objects.all().delete()
    print(f"All objects in bucket {bucket_name} deleted.")
    
    # Deleting the bucket itself
    bucket.delete()
    print(f"S3 bucket {bucket_name} deleted.")

def delete_sns_topic(topic_arn):
    sns = boto3.client('sns')
    
    # Unsubscribe all subscriptions to the topic
    subscriptions = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    for sub in subscriptions['Subscriptions']:
        sns.unsubscribe(SubscriptionArn=sub['SubscriptionArn'])
    
    # Delete the SNS topic
    sns.delete_topic(TopicArn=topic_arn)
    print(f"SNS topic {topic_arn} deleted.")

def teardown_infrastructure(asg_name, lb_arn, tg_arn, instance_ids, bucket_name, sns_topic_arn):
    # Deleteting Auto Scaling Group
    delete_auto_scaling_group(asg_name)
    
    # Deleteting Load Balancer and Target Group
    delete_load_balancer(lb_arn, tg_arn)
    
    # Terminating EC2 Instances
    terminate_ec2_instances(instance_ids)
    
    # Deleteing S3 Bucket
    empty_and_delete_s3_bucket(bucket_name)
    
    # Deleteing SNS Topic
    delete_sns_topic(sns_topic_arn)

if __name__ == "__main__":
    # Deploying infrastructure
    lb_arn, tg_arn, instance_ids, sns_topic_arn = deploy_infrastructure()
    
    # We need to Uncomment the below line to teardown infrastructure
    # teardown_infrastructure('my-asg', lb_arn, tg_arn, instance_ids, 'your-webapp-bucket', sns_topic_arn)

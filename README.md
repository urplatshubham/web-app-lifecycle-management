# web-app-lifecycle-management

This project provides an automated approach to launching, managing, and tearing down a complete web application infrastructure on AWS, using Python's `boto3` library. It includes functionalities like creating an EC2 instance, setting up an Application Load Balancer (ALB), configuring an Auto Scaling Group (ASG), and managing SNS notifications. The infrastructure can be easily deployed and torn down with a few commands.

## Features

- **EC2 Instance Launch**: Automatically launch an EC2 instance and configure it with a basic NGINX web server.
- **Application Load Balancer**: Deploy an Application Load Balancer and register the EC2 instance to balance incoming traffic.
- **Auto Scaling Group**: Automatically scale instances based on traffic and CPU utilization.
- **SNS Notifications**: Receive email alerts for scaling events and infrastructure health.
- **Infrastructure Teardown**: Cleanly remove all resources including EC2 instances, load balancer, auto-scaling group, S3 bucket, and SNS topics.

## Prerequisites

Before running this script, we have to make sure that the following is available:

- AWS CLI installed and configured on your system. Run `aws configure` to set up your credentials.
- A valid AWS account with appropriate permissions to create and manage EC2, S3, ELB, Auto Scaling, and SNS resources.
- Python 3 installed on your machine.
- The following Python libraries:
  - `boto3`
  - `botocore`

Install the required libraries by running:

```bash
pip install boto3 botocore
```

## Setup

1. **Clone the Repository**

   Clone this repository to your local machine:

   ```bash
   git clone https://github.com/urplatshubham/web-app-lifecycle-management.git
   cd web-app-lifecycle-management
   ```

2. **Update the Script**

   Before running the script, make sure to update certain placeholders with your specific AWS resource information, such as:
   - **AMI ID**: Modify the AMI ID to match your region or use a script to dynamically fetch the latest AMI.
   - **Key Pair**: Updated the `KeyName` with the name of your AWS key pair. I have used Shubham-instance which was existed on my AWS console.
   - **Security Group ID**: Specify the correct security group to allow traffic to the EC2 instance. I have used the SG from AWS console through already existing instances configured with SG.
   - **Subnets**: Specify the subnet IDs where you want to deploy the EC2 instance and load balancer. I have used the SG from AWS console through already existing instances configured with EC2 instance.

## Usage

### 1. Deploying the Infrastructure

The main function `deploy_infrastructure()` creates the following:
- An EC2 instance with an NGINX server.
- An S3 bucket for storing any static files.
- An Application Load Balancer to manage incoming traffic.
- An Auto Scaling Group to automatically scale the infrastructure.
- SNS notifications for monitoring the health of the infrastructure.

Run the script to deploy the infrastructure:

```bash
python Infra_Code.py
```

### 2. Tearing Down the Infrastructure

Once you're done using the resources, you can cleanly tear down the entire infrastructure by uncommenting the teardown section and running:

```bash
python Infra_Code.py
```

This will:
- Delete the Auto Scaling Group.
- Deregister and delete the Application Load Balancer and Target Group.
- Terminate the EC2 instances.
- Empty and delete the S3 bucket.
- Unsubscribe and delete SNS topics.

### 3. Customize the Script

You can modify the following to suit your needs:
- **EC2 Instance Type**: Change the instance type in the `launch_ec2()` function.
- **Scaling Policies**: Adjust the scaling policies to handle different metrics.
- **User Data**: Modify the `user_data_script` in `launch_ec2()` to install additional software on the EC2 instance.

## Project Structure

```bash
.
├── README.md               # Documentation for the project
├── Infra_Code.py                 # Main Python script for deploying and tearing down infrastructure
```

## Key Functions

- **create_s3_bucket()**: Creating an S3 bucket for storing web application files.
- **launch_ec2()**: Launching an EC2 instance and configures a basic NGINX web  for reverse proxy.
- **create_load_balancer()**: Setting up an Application Load Balancer and registers EC2 instances to it.
- **configure_asg()**: Configuring an Auto Scaling Group to automatically scale EC2 instances.
- **setup_sns()**: Configuring SNS for notifications.
- **teardown_infrastructure()**: Tears down all resources created during deployment.

## Notes

- The script uses Amazon Linux 2 AMI by default, but can be customized to use other AMIs (such as Ubuntu or Windows).
- I here ensured that the IAM role associated with your AWS CLI or SDK has sufficient permissions to create and manage the required resources.

## Troubleshooting

- **Permission Issues**: I here ensure that the AWS credentials have the necessary permissions to create and manage EC2, S3, Auto Scaling, ELB, and SNS resources.
- **Resource Limits**: If any errors, we can check one's AWS account's service limits if you encounter errors related to instance limits, bucket creation, or other resources.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


#!/usr/bin/env python3
import os
import boto3

from aws_cdk import core as cdk

from miniwdl_gwfcore_studio.miniwdl_gwfcore_studio_stack import (
    MiniwdlGwfcoreStudioStack,
)

DEFAULT_GWFCORE_VERSION = "v3.0.7"
gwfcore_version = os.environ.get("GWFCORE_VERSION", DEFAULT_GWFCORE_VERSION)

env = {}
if "CDK_DEFAULT_ACCOUNT" in os.environ:
    env["account"] = os.environ["CDK_DEFAULT_ACCOUNT"]
if "CDK_DEFAULT_REGION" in os.environ:
    env["region"] = os.environ["CDK_DEFAULT_REGION"]

###################################################################################################
# First perform some ops that aren't convenient to do via CDK/Cfn for various reasons.
###################################################################################################

# Describe existing studio domain+user for VPC/IAM/EFS details
studio_domain_id = os.environ.get("STUDIO_DOMAIN_ID", None)
studio_user_profile_name = os.environ.get("STUDIO_USER_PROFILE_NAME", None)
assert (
    studio_domain_id and studio_user_profile_name
), "set environment STUDIO_DOMAIN_ID and STUDIO_USER_PROFILE_NAME to reflect SageMaker Studio"
client_opts = {}
if "region" in env:
    client_opts["region_name"] = env["region"]
sagemaker = boto3.client("sagemaker", **client_opts)
domain_desc = sagemaker.describe_domain(DomainId=studio_domain_id)
user_profile_desc = sagemaker.describe_user_profile(
    DomainId=studio_domain_id, UserProfileName=studio_user_profile_name
)

# Find the Studio EFS' security group, named "security-group-for-inbound-nfs-{studio_domain_id}"
# Nice-to-have: describe Studio EFS' mount targets to double-check they're in this security group.
ec2 = boto3.client("ec2", **client_opts)
sg_desc = ec2.describe_security_groups(
    Filters=[
        dict(
            Name="group-name",
            Values=[f"security-group-for-inbound-nfs-{studio_domain_id}"],
        )
    ]
)
assert (
    len(sg_desc.get("SecurityGroups", [])) == 1
), f"Failed to look up SageMaker Studio EFS security group named 'security-group-for-inbound-nfs-{studio_domain_id}'"
studio_efs_sg_id = sg_desc["SecurityGroups"][0]["GroupId"]

# Log the detected details
print(f"studio_domain_id = {studio_domain_id}")
print(f"studio_user_profile_name = {studio_user_profile_name}")
detected = dict(
    vpc_id=domain_desc["VpcId"],
    studio_efs_id=domain_desc["HomeEfsFileSystemId"],
    studio_efs_uid=user_profile_desc["HomeEfsFileSystemUid"],
    studio_efs_sg_id=studio_efs_sg_id,
)
for k, v in detected.items():
    print(f"{k} = {v}")

# Add necessary policies to the Studio ExecutionRole. We don't do this through CDK because of:
#   https://github.com/aws/aws-cdk/blob/486f2e5518ab5abb69a3e3986e4f3581aa42d15b/packages/%40aws-cdk/aws-iam/lib/role.ts#L225-L227
studio_execution_role_arn = user_profile_desc.get("UserSettings", {}).get("ExecutionRole", "")
assert studio_execution_role_arn.startswith(
    "arn:aws:iam::"
), "Failed to detect SageMaker Studio ExecutionRole ARN"
studio_execution_role_name = studio_execution_role_arn[studio_execution_role_arn.rindex("/") + 1 :]
iam = boto3.client("iam", **client_opts)

for policy_arn in (
    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
    "arn:aws:iam::aws:policy/AWSBatchFullAccess",
    "arn:aws:iam::aws:policy/AmazonElasticFileSystemFullAccess",
):
    # TODO: constrain these to the specific EFS & Batch queues
    print(f"Adding to {studio_execution_role_name}: {policy_arn}")
    iam.attach_role_policy(
        RoleName=studio_execution_role_arn[studio_execution_role_arn.rindex("/") + 1 :],
        PolicyArn=policy_arn,
    )


###################################################################################################
# CDK stack to do the rest
###################################################################################################


app = cdk.App()
MiniwdlGwfcoreStudioStack(
    app,
    "MiniwdlGwfcoreStudioStack",
    gwfcore_version=gwfcore_version,
    env=env,
    **detected,
)

app.synth()

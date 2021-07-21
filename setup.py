import setuptools
from version import get_version

MINIWDL_AWS_MIN_VERSION = "0.0.1"
CDK_MIN_VERSION = "1.110.0"

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="miniwdl-aws-studio",
    version=get_version(),
    description="AWS CDK app to add miniwdl+GWFCore to existing SageMaker Studio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Wid L. Hacker",
    package_dir={"": "miniwdl_gwfcore_studio"},
    packages=setuptools.find_packages(where="miniwdl_gwfcore_studio"),
    install_requires=["boto3>=1.17", f"miniwdl-aws>={MINIWDL_AWS_MIN_VERSION}"]
    + [
        f"aws-cdk.{m}>={CDK_MIN_VERSION}"
        for m in ("core", "aws_iam", "aws_ec2", "aws_efs", "cloudformation_include")
    ],
    python_requires=">=3.6",
)

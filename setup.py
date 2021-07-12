import setuptools


with open("README.md") as fp:
    long_description = fp.read()

CDK_MIN_VERSION = "1.110.0"

setuptools.setup(
    name="miniwdl-aws-studio",
    version="0.0.1",
    description="AWS CDK app to add miniwdl+GWFCore to existing SageMaker Studio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Wid L. Hacker",
    package_dir={"": "miniwdl_gwfcore_studio"},
    packages=setuptools.find_packages(where="miniwdl_gwfcore_studio"),
    install_requires=["boto3"]
    + [
        f"aws-cdk.{m}>={CDK_MIN_VERSION}"
        for m in ("core", "aws_iam", "aws_ec2", "aws_efs", "cloudformation_include")
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)

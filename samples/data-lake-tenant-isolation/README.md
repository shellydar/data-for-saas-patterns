# Data Lake tenant Isolation


Software companies can leverage data lakes to store and manage large volumes of structured and unstructured data from various sources. By consolidating data into a centralized repository, data lakes enable companies to analyze and extract insights from diverse data types, including application logs, sensor data, customer interactions, and more. This approach facilitates data-driven decision-making, improves operational efficiency, and fosters innovation by allowing companies to explore new business opportunities and develop data-driven products and services. Additionally, data lakes can serve as a foundation for implementing advanced analytics, machine learning, and artificial intelligence initiatives.

In this sample we will create a Data Lake in S3, we will create Lake Formation permissions based on tags and allow the permissions to change based on the specific session.

# Resources

This sample creates the following resources:

- S3 Bucket for the dataset sample
- Lake Formation with initial tags and permissions
- Compute layer stack
    - API GW
    - Cognito
    - Lambda for creating new tags (as part of customer on-boarding)
    - Lambda for reading the data based on the tags of the tenant

# Requirements

* [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
* [Git Installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [Python 3](https://www.python.org/downloads/) installed.
* [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/cli.html) installed and configured

## Deployment Instructions

1. Clone the GitHub repository:
    ``` 
    git clone https://github.com/aws-samples/data-for-saas-patterns.git
    ```
2. Change directory to the cdk project :
    ```
    cd data-for-saas-patterns/samples/data-lake-tenant-isolation/
    ```
3. Create virtual environment

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the .env
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

4. install the required dependencies.

```
$ pip install -r requirements.txt
```
5. Configure AWS CDK to bootstrap the AWS account:
    ```
    cdk bootstrap <account-id>/<region>
    ```
6. From the command line, use AWS CDK to deploy the stack: 
    ```
    cdk deploy
    ```
    
## Clean up
to clean up the resources created run the destroy command
    ```
    cdk destroy
    ```
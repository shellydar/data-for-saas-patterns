import boto3

def create_temp_tenant_session(access_role_arn, session_name, tenant_id, duration_sec):
    """
    Create a temporary session
    :param access_role_arn: The ARN of the role that the caller is assuming
    :param session_name: An identifier for the assumed session
    :param tenant_id: The tenant identifier the session is created for
    :param duration_sec: The duration, in seconds, of the temporary session
    :return: The session object that allows you to create service clients and resources
    """
    sts = boto3.client('sts')
    assume_role_response = sts.assume_role(
        RoleArn=access_role_arn,
        DurationSeconds=duration_sec,
        RoleSessionName=session_name,
        Tags=[
            {
                'Key': 'TenantID',
                'Value': tenant_id
            }
        ]
    )
    session = boto3.Session(aws_access_key_id=assume_role_response['Credentials']['AccessKeyId'],
                    aws_secret_access_key=assume_role_response['Credentials']['SecretAccessKey'],
                    aws_session_token=assume_role_response['Credentials']['SessionToken'])
    return session
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) to use Amazon API Gateway to
create a REST API backed by a Lambda function.

Instead of using the low-level Boto3 client APIs shown in this example, you can use
AWS Chalice to more easily create a REST API.

    For a working code example, see the `lambda/chalice_examples/lambda_rest` example
    in this GitHub repo.

    For more information about AWS Chalice, see https://github.com/aws/chalice.
"""

import calendar
import datetime
import json
import logging
import time
import boto3
from botocore.exceptions import ClientError
import requests

import Lambda.lambda_basics as lambda_basics

logger = logging.getLogger(__name__)


def create_rest_api(
        apigateway_client, api_name, api_base_path, api_stage,
        account_id, lambda_client, lambda_function_arn):
    """
    Creates a REST API in Amazon API Gateway. The REST API is backed by the specified AWS Lambda function.

    1. Creates a REST API in Amazon API Gateway.
    2. Creates a '/canaal-api' resource in the REST API.
    3. Creates a method that accepts all HTTP actions and passes them through to the specified AWS Lambda function.
    4. Deploys the REST API to Amazon API Gateway.
    5. Adds a resource policy to the AWS Lambda function that grants permission to let Amazon API Gateway call the AWS Lambda function.

    :param apigateway_client: The Boto3 Amazon API Gateway client object.
    :param api_name: The name of the REST API.
    :param api_base_path: The base path part of the REST API URL.
    :param api_stage: The deployment stage of the REST API.
    :param account_id: The ID of the owning AWS account.
    :param lambda_client: The Boto3 AWS Lambda client object.
    :param lambda_function_arn: The Amazon Resource Name (ARN) of the AWS Lambda
                                function that is called by Amazon API Gateway to
                                handle REST requests.
    :return: The ID of the REST API. This ID is required by most Amazon API Gateway methods.
    """
    try:
        response = apigateway_client.create_rest_api(name=api_name)
        api_id = response['id']
        logger.info(f"Create REST API {api_name} with ID {api_id}.")
    except ClientError:
        logger.exception(f"Couldn't create REST API {api_name}.")
        raise

    try:
        response = apigateway_client.get_resources(restApiId=api_id)
        root_id = next(item['id'] for item in response['items'] if item['path'] == '/')
        logger.info(f"Found root resource of the REST API with ID {root_id}.")
    except ClientError:
        logger.exception("Couldn't get the ID of the root resource of the REST API.")
        raise

    try:
        response = apigateway_client.create_resource(
            restApiId=api_id, parentId=root_id, pathPart=api_base_path)
        base_id = response['id']
        logger.info(f"Created base path {api_base_path} with ID {base_id}.")
    except ClientError:
        logger.exception(f"Couldn't create a base path for {api_base_path}.")
        raise

    try:
        apigateway_client.put_method(
            restApiId=api_id, resourceId=base_id, httpMethod='ANY',
            authorizationType='NONE')
        logger.info("Created a method that accepts all HTTP verbs for the base resource.")
    except ClientError:
        logger.exception("Couldn't create a method for the base resource.")
        raise

    lambda_uri = \
        f'arn:aws:apigateway:{apigateway_client.meta.region_name}:lambda:path/2015-03-31/functions/{lambda_function_arn}/invocations'
    try:
        apigateway_client.put_integration(
            restApiId=api_id, resourceId=base_id, httpMethod='ANY', type='AWS_PROXY',
            integrationHttpMethod='POST', uri=lambda_uri)
        logger.info(f"Set function {lambda_function_arn} as integration destination for the base resource.")
    except ClientError:
        logger.exception(f"Couldn't set function {lambda_function_arn} as integration destination.")
        raise

    try:
        apigateway_client.create_deployment(restApiId=api_id, stageName=api_stage)
        logger.info(f"Deployed REST API {api_id}.")
    except ClientError:
        logger.exception(f"Couldn't deploy REST API {api_id}.")
        raise

    source_arn = \
        f'arn:aws:execute-api:{apigateway_client.meta.region_name}:{account_id}:{api_id}/*/*/{api_base_path}'
    try:
        lambda_client.add_permission(
            FunctionName=lambda_function_arn, StatementId=f'canaal-invoke',
            Action='lambda:InvokeFunction', Principal='apigateway.amazonaws.com',
            SourceArn=source_arn)
        logger.info(f"Granted permission to let Amazon API Gateway invoke function {lambda_function_arn} from {source_arn}.")
    except ClientError:
        logger.exception(f"Couldn't add permission to let Amazon API Gateway invoke {lambda_function_arn}.")
        raise

    return api_id


def construct_api_url(api_id, region, api_stage, api_base_path):
    """
    Constructs the URL of the REST API.

    :param api_id: The ID of the REST API.
    :param region: The AWS Region where the REST API was created.
    :param api_stage: The deployment stage of the REST API.
    :param api_base_path: The base path part of the REST API.
    :return: The full URL of the REST API.
    """
    api_url = \
        f'https://{api_id}.execute-api.{region}.amazonaws.com/{api_stage}/{api_base_path}'
    logger.info(f"Constructed REST API base URL: {api_url}.")
    return api_url


def delete_rest_api(apigateway_client, api_id):
    """
    Deletes a REST API and all of its resources from Amazon API Gateway.

    :param apigateway_client: The Boto3 Amazon API Gateway client.
    :param api_id: The ID of the REST API.
    """
    try:
        apigateway_client.delete_rest_api(restApiId=api_id)
        logger.info(f"Deleted REST API {api_id}.")
    except ClientError:
        logger.exception(f"Couldn't delete REST API {api_id}.")
        raise

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

AWS Lambda function that handles calls from an Amazon API Gateway REST API.
"""

import json
import boto3
import uuid

def lambda_handler(event, context):

    return {
        'body':event,
        'statusCode': 200,
    }

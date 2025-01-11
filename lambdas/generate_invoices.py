import os
import logging

import boto3

from db.dynamo_schemas import LambdaMetrics
from db.dynamo_operations import DDB
from utils.stark_bank import generate_invoices
from utils.errors import log_error

ddb = DDB()

eventbridge = boto3.client('events')
lambda_client = boto3.client('lambda')

TABLE_NAME = os.getenv("DYNAMO_TABLE_NAME")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
REGION = os.getenv("REGION")
RULE_NAME = "SelfSchedulerRule"
TARGET_ID = "SelfSchedulerTarget"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        lambda_arn = context.invoked_function_arn
        lambda_metric = update_lambda_call_count()

        generate_invoices()

        if lambda_metric.callCount == 1:
            logger.info("Creating scheduler")
            create_scheduler(lambda_arn)

        if lambda_metric.callCount >= 8:
            logger.info("Max executions reached, deleting scheduler")
            delete_scheduler(lambda_arn)
            ddb.delete(lambda_metric)
    
        return {"statusCode": 200, "body": f"Execution count: {lambda_metric.callCount}"}
    except Exception as e:
        log_error(event, context, str(e))

def update_lambda_call_count() -> LambdaMetrics:
    lambda_metric = ddb.load(LambdaMetrics, "InvoiceGeneratorLambda")

    if not lambda_metric:
        lambda_metric = LambdaMetrics(lambdaName="InvoiceGeneratorLambda", callCount=0)
    
    lambda_metric.callCount += 1
    ddb.save(lambda_metric)

    return lambda_metric

def create_scheduler(lambda_arn):
    eventbridge.put_rule(
        Name=RULE_NAME,
        ScheduleExpression="cron(0 */3 * * ? *)",
        State="ENABLED"
    )

    eventbridge.put_targets(
        Rule=RULE_NAME,
        Targets=[
            {
                'Id': TARGET_ID,
                'Arn': lambda_arn
            }
        ]
    )

    lambda_client.add_permission(
        FunctionName=lambda_arn.split(':')[-1],
        StatementId=f"{RULE_NAME}-Invoke",
        Action="lambda:InvokeFunction",
        Principal="events.amazonaws.com",
        SourceArn=f"arn:aws:events:{REGION}:{ACCOUNT_ID}:rule/{RULE_NAME}"
    )

def delete_scheduler(lambda_arn):
    eventbridge.remove_targets(
        Rule=RULE_NAME,
        Ids=[TARGET_ID]
    )

    eventbridge.delete_rule(
        Name=RULE_NAME
    )

    lambda_client.remove_permission(
        FunctionName=lambda_arn.split(':')[-1],
        StatementId=f"{RULE_NAME}-Invoke"
    )

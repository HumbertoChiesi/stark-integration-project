from db.dynamo_schemas import LambdaErrorsLog
from db.dynamo_operations import DDB

ddb = DDB()

def log_error(event, context, error_message):
    """# Log Error
    Logs error details to a DynamoDB table for tracking Lambda errors.
    ## Parameters (required):
    - event [dict]: The event data passed to the Lambda function. an AWS event.
    - context [LambdaContext]: The context object passed to the Lambda function, which contains metadata about the function invocation.
    - error_message [str]: The error message.
    ## Return:
    - None
    """
    payload = event
    lambda_name = context.function_name    
    execution_id = context.aws_request_id

    log = LambdaErrorsLog(
        lambdaName=lambda_name,
        executionId=execution_id,
        payload=str(payload),
        errorMessage=error_message
    )

    ddb.save(log)



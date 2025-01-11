import json
from utils.stark_bank import create_transfer
from utils.errors import log_error

def lambda_handler(event, context):
    client_ip = event.get('requestContext', {}).get('http', {}).get('sourceIp')
    if client_ip != "35.247.226.240":
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "Unauthorized IP address."})
        }

    try:
        body = json.loads(event["body"])
        event = body.get("event", {})
        log = event.get("log", {})
        invoice = log.get("invoice", {})
        
        if event.get("subscription") == "invoice" and log.get("type") == "credited" and invoice.get("status") == "paid":
            amount = invoice.get("amount", 0) / 100
            fee = invoice.get("fee", 0) / 100
            net_amount = int((amount - fee) * 100) 

            create_transfer(net_amount)

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Transfer successful"})
            }

        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Event is not a credited, paid invoice."})
        }

    except Exception as e:
        log_error(event, context, str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error", "error": str(e)})
        }
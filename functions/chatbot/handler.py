import json
import boto3
from openai import OpenAI


import os

from botocore.exceptions import BotoCoreError, ClientError

# Function to retrieve OpenAI API Key securely
def get_openai_key():
    secret_name = "prod/Bavarde/OpenAIKey"
    region_name = "eu-west-1"  # Change to your region
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except (BotoCoreError, ClientError) as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    

    secret_string = get_secret_value_response['SecretString']
    print(secret_string)
    secret = json.loads(secret_string)  # Parse JSON
    return secret.get('OPENAI_API_KEY')

# Set API Key
api_key = get_openai_key()
client = OpenAI(api_key=api_key)

print("API Key loaded")

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        user_message = body.get("message", "")

        if not user_message:
            return {"statusCode": 400, "body": json.dumps({"error": "Message cannot be empty."})}

        # Call OpenAI API
        response = client.chat.completions.create(model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Tu es une femme française amicale et naturelle."},
            {"role": "user", "content": user_message}
        ])

        ai_response = response.choices[0].message.content

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"response": ai_response})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

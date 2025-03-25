import json
import jwt  # PyJWT library
import os

# Store this securely! This should be the secret generated earlier.
# Fetch JWT Secret from environment
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret")

def lambda_handler(event, context):
    try:
        token = event["authorizationToken"].split("Bearer ")[-1]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Check claims (optional, you can enforce roles, expiry, etc.)
        if "user" not in decoded_token:
            raise Exception("Invalid token")

        # Allow request
        return {
            "principalId": decoded_token["user"],
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": event["methodArn"]
                    }
                ]
            }
        }

    except Exception as e:
        # Deny request if token is invalid
        return {
            "principalId": "unauthorized",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Deny",
                        "Resource": event["methodArn"]
                    }
                ]
            }
        }

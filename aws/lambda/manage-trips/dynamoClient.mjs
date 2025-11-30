import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

const docClient = new DynamoDBClient({
  region: process.env.LAMBDA_AWS_REGION,
});

export const client = DynamoDBDocumentClient.from(docClient);
export const TABLE_NAME = process.env.TABLE_NAME;
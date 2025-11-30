import {
  GetItemCommand,
  DeleteItemCommand,
  ScanCommand,
  PutItemCommand
} from "@aws-sdk/client-dynamodb";
import { marshall, unmarshall } from "@aws-sdk/util-dynamodb";
import crypto from "node:crypto";
import {
  normalizePayload,
  buildErrorResponse,
  buildSuccessResponse
} from "./utils.mjs";
import { client, TABLE_NAME } from "./dynamoClient.mjs";

const success = buildSuccessResponse;
const error = buildErrorResponse;

export const handler = async (event) => {
  let body = {};

  try {
    body = normalizePayload(event);
  } catch (err) {
    if (err.message === "INVALID_JSON_BODY") {
      return error(400, "Invalid JSON body supplied");
    }
    return error(500, "Failed to process request body");
  }

  const method = event.requestContext?.http?.method;
  const path = event.rawPath;
  const tripId = event.pathParameters?.tripId || undefined;

  try {
    // ---- GET /api/trips ----
    if (method === "GET" && path === "/api/trips") {
      const params = {
        TableName: TABLE_NAME
      };

      const result = await client.send(new ScanCommand(params));

      const items =
        result.Items?.map((item) => unmarshall(item)) || [];

      return success(200, items);
    }

    // ---- GET /api/trips/{tripId} ----
    if (method === "GET" && tripId) {
      const result = await client.send(
        new GetItemCommand({
          TableName: TABLE_NAME,
          Key: {
            tripId: { S: tripId }
          }
        })
      );

      if (!result.Item) {
        return error(404, "Trip not found");
      }

      return success(200, item);
    }

    // ---- POST /api/trips ----
    if (method === "POST" && path === "/api/trips") {
      if (!body) {
        return error(400, "Request body is required");
      }

      const now = new Date().toISOString();
      const newTripId = crypto.randomUUID();

      const item = {
        tripId: newTripId,
        userId: body.userId,
        generatedAt: now,
        status: body.status || "planned",
        basics: body.basics || null,
        preferences: body.preferences || null,
        planResult: body.planResult || null,
        map: body.map || null
      };

      await client.send(
        new PutItemCommand({
          TableName: TABLE_NAME,
          Item: marshall(item, { removeUndefinedValues: true }),
          ConditionExpression: "attribute_not_exists(tripId)"
        })
      );

      return success(201, item);
    }

    // ---- DELETE /api/trips/{tripId} ----
    if (method === "DELETE" && tripId) {
      // voliteľne: načítať a skontrolovať userId pred delete
      await client.send(
        new DeleteItemCommand({
          TableName: TABLE_NAME,
          Key: {
            tripId: { S: tripId }
          }
        })
      );

      return success(204, null);
    }

    return error(404, "Not found");
  } catch (err) {
    console.error("Handler error:", err);
    return error(500, "Internal server error");
  }
};

export const normalizePayload = (event) => {
    // First make sure body is a string before trying to trim it
    if (typeof event?.body === "string" && event.body.trim()) {
        try {
            return JSON.parse(event.body);
        } catch {
            throw new Error("INVALID_JSON_BODY");
        }
    }

    if (event?.body && typeof event.body === "object") {
        return event.body;
    }

    return event ?? {};
};
// Build a successful response
export const buildSuccessResponse = (statusCode, payload) => ({
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
});
// Build an error response
export const buildErrorResponse = (statusCode, message, details) => ({
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ error: message, ...(details ? { details } : {}) }),
});
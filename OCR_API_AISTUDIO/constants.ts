
// This key must be configured in the environment.
// The user provided the variable name SCANDOCFLOW_API_KEY.
// export const SCANDOCFLOW_API_KEY = process.env.SCANDOCFLOW_API_KEY; // Removed

export const UPLOAD_URL = "https://backend.scandocflow.com/v1/api/documents/extractAsync";
export const STATUS_URL = "https://backend.scandocflow.com/v1/api/documents/status";

export const MAX_POLL_TIME_MS = 120000; // 2 minutes
export const POLL_INTERVAL_MS = 5000; // 5 seconds
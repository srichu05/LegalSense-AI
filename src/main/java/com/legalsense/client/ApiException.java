package com.legalsense.client;

import com.legalsense.model.ErrorResponse;

/**
 * Exception thrown when an API request fails, either due to network issues,
 * HTTP error responses, or response parsing errors.
 */
public class ApiException extends Exception {

    private final int statusCode;
    private final String errorCode;
    private final String rawResponseBody;

    public ApiException(String message) {
        this(0, "CLIENT_ERROR", message, null, null);
    }

    public ApiException(String message, Throwable cause) {
        this(0, "CLIENT_ERROR", message, null, cause);
    }

    public ApiException(int statusCode, String errorCode, String message) {
        this(statusCode, errorCode, message, null, null);
    }

    public ApiException(int statusCode, String errorCode, String message, String rawResponseBody) {
        this(statusCode, errorCode, message, rawResponseBody, null);
    }

    public ApiException(int statusCode, String errorCode, String message, String rawResponseBody, Throwable cause) {
        super(formatMessage(statusCode, errorCode, message), cause);
        this.statusCode = statusCode;
        this.errorCode = errorCode != null ? errorCode : "UNKNOWN_ERROR";
        this.rawResponseBody = rawResponseBody;
    }

    private static String formatMessage(int statusCode, String errorCode, String message) {
        if (statusCode > 0 && errorCode != null) {
            return String.format("[%d %s] %s", statusCode, errorCode, message != null ? message : "No details provided");
        } else if (errorCode != null) {
            return String.format("[%s] %s", errorCode, message != null ? message : "No details provided");
        }
        return message != null ? message : "An unexpected API error occurred.";
    }

    public int getStatusCode() {
        return statusCode;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public String getRawResponseBody() {
        return rawResponseBody;
    }

    public String getUserFacingMessage() {
        if (statusCode == 0) {
            return "Unable to connect to LegalSense backend service. Please verify the backend is running and the URL is correct.";
        }
        if (getMessage() != null && !getMessage().isBlank()) {
            return getMessage();
        }
        return "Backend returned error status " + statusCode;
    }
}

package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Standard error response envelope matching API_SPEC.md § 5.
 */
public class ErrorResponse {

    @JsonProperty("error")
    private ErrorDetail error;

    public ErrorResponse() {
    }

    public ErrorResponse(String code, String message) {
        this.error = new ErrorDetail(code, message);
    }

    public ErrorDetail getError() {
        return error;
    }

    public void setError(ErrorDetail error) {
        this.error = error;
    }

    public static class ErrorDetail {

        @JsonProperty("code")
        private String code;

        @JsonProperty("message")
        private String message;

        public ErrorDetail() {
        }

        public ErrorDetail(String code, String message) {
            this.code = code;
            this.message = message;
        }

        public String getCode() {
            return code;
        }

        public void setCode(String code) {
            this.code = code;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }
    }
}

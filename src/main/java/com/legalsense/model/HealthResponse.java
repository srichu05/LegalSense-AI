package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Health check response from GET /health.
 */
public class HealthResponse {

    @JsonProperty("status")
    private String status;

    @JsonProperty("service")
    private String service;

    @JsonProperty("wsd_ready")
    private boolean wsdReady;

    @JsonProperty("llm_enabled")
    private boolean llmEnabled;

    public HealthResponse() {
    }

    public HealthResponse(String status, String service, boolean wsdReady, boolean llmEnabled) {
        this.status = status;
        this.service = service;
        this.wsdReady = wsdReady;
        this.llmEnabled = llmEnabled;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getService() {
        return service;
    }

    public void setService(String service) {
        this.service = service;
    }

    public boolean isWsdReady() {
        return wsdReady;
    }

    public void setWsdReady(boolean wsdReady) {
        this.wsdReady = wsdReady;
    }

    public boolean isLlmEnabled() {
        return llmEnabled;
    }

    public void setLlmEnabled(boolean llmEnabled) {
        this.llmEnabled = llmEnabled;
    }

    public boolean isHealthy() {
        return "ok".equalsIgnoreCase(status) && wsdReady;
    }
}

package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

/**
 * Response payload for POST /api/v1/analyze.
 */
public class AnalyzeResponse {

    @JsonProperty("request_id")
    private String requestId;

    @JsonProperty("results")
    private List<WsdResultDto> results = new ArrayList<>();

    @JsonProperty("warnings")
    private List<String> warnings = new ArrayList<>();

    public AnalyzeResponse() {
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public List<WsdResultDto> getResults() {
        return results != null ? results : new ArrayList<>();
    }

    public void setResults(List<WsdResultDto> results) {
        this.results = results;
    }

    public List<String> getWarnings() {
        return warnings != null ? warnings : new ArrayList<>();
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}

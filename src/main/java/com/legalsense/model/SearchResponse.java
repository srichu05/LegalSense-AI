package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

/**
 * Response payload for POST /api/v1/search.
 */
public class SearchResponse {

    @JsonProperty("query")
    private String query;

    @JsonProperty("results")
    private List<SearchResultDto> results = new ArrayList<>();

    @JsonProperty("warnings")
    private List<String> warnings = new ArrayList<>();

    public SearchResponse() {
    }

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public List<SearchResultDto> getResults() {
        return results != null ? results : new ArrayList<>();
    }

    public void setResults(List<SearchResultDto> results) {
        this.results = results;
    }

    public List<String> getWarnings() {
        return warnings != null ? warnings : new ArrayList<>();
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}

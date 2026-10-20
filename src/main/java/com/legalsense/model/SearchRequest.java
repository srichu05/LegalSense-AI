package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Request payload for POST /api/v1/search.
 */
public class SearchRequest {

    @JsonProperty("query")
    private String query;

    @JsonProperty("top_k")
    private int topK = 5;

    @JsonProperty("use_llm")
    private boolean useLlm = false;

    public SearchRequest() {
    }

    public SearchRequest(String query) {
        this(query, 5, false);
    }

    public SearchRequest(String query, int topK, boolean useLlm) {
        this.query = query;
        this.topK = topK;
        this.useLlm = useLlm;
    }

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public int getTopK() {
        return topK;
    }

    public void setTopK(int topK) {
        this.topK = topK;
    }

    public boolean isUseLlm() {
        return useLlm;
    }

    public void setUseLlm(boolean useLlm) {
        this.useLlm = useLlm;
    }
}

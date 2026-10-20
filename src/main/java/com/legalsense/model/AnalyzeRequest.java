package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Request payload for POST /api/v1/analyze.
 */
public class AnalyzeRequest {

    @JsonProperty("text")
    private String text;

    @JsonProperty("target_word")
    private String targetWord;

    @JsonProperty("use_llm")
    private boolean useLlm;

    public AnalyzeRequest() {
    }

    public AnalyzeRequest(String text) {
        this(text, null, false);
    }

    public AnalyzeRequest(String text, String targetWord, boolean useLlm) {
        this.text = text;
        this.targetWord = targetWord;
        this.useLlm = useLlm;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public String getTargetWord() {
        return targetWord;
    }

    public void setTargetWord(String targetWord) {
        this.targetWord = targetWord;
    }

    public boolean isUseLlm() {
        return useLlm;
    }

    public void setUseLlm(boolean useLlm) {
        this.useLlm = useLlm;
    }
}

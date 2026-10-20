package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Curated legal glossary entry with explicit provenance.
 */
public class GlossaryEntryDto {

    @JsonProperty("term")
    private String term;

    @JsonProperty("definition")
    private String definition;

    @JsonProperty("jurisdiction")
    private String jurisdiction;

    @JsonProperty("source")
    private String source;

    @JsonProperty("usage_example")
    private String usageExample;

    @JsonProperty("limitations")
    private String limitations;

    public GlossaryEntryDto() {
    }

    public String getTerm() {
        return term;
    }

    public void setTerm(String term) {
        this.term = term;
    }

    public String getDefinition() {
        return definition;
    }

    public void setDefinition(String definition) {
        this.definition = definition;
    }

    public String getJurisdiction() {
        return jurisdiction;
    }

    public void setJurisdiction(String jurisdiction) {
        this.jurisdiction = jurisdiction;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getUsageExample() {
        return usageExample;
    }

    public void setUsageExample(String usageExample) {
        this.usageExample = usageExample;
    }

    public String getLimitations() {
        return limitations;
    }

    public void setLimitations(String limitations) {
        this.limitations = limitations;
    }
}

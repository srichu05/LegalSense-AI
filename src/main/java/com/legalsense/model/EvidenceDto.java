package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

/**
 * Overlap evidence contributing to a candidate sense score.
 */
public class EvidenceDto {

    @JsonProperty("candidate_synset_id")
    private String candidateSynsetId;

    @JsonProperty("overlap_tokens")
    private List<String> overlapTokens = new ArrayList<>();

    @JsonProperty("overlap_source")
    private String overlapSource;

    @JsonProperty("contribution")
    private double contribution;

    public EvidenceDto() {
    }

    public String getCandidateSynsetId() {
        return candidateSynsetId;
    }

    public void setCandidateSynsetId(String candidateSynsetId) {
        this.candidateSynsetId = candidateSynsetId;
    }

    public List<String> getOverlapTokens() {
        return overlapTokens != null ? overlapTokens : new ArrayList<>();
    }

    public void setOverlapTokens(List<String> overlapTokens) {
        this.overlapTokens = overlapTokens;
    }

    public String getOverlapSource() {
        return overlapSource;
    }

    public void setOverlapSource(String overlapSource) {
        this.overlapSource = overlapSource;
    }

    public double getContribution() {
        return contribution;
    }

    public void setContribution(double contribution) {
        this.contribution = contribution;
    }
}

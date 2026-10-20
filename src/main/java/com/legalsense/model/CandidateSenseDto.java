package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * A candidate WordNet sense for a term with score, rank, and relations.
 */
public class CandidateSenseDto {

    @JsonProperty("source")
    private String source;

    @JsonProperty("synset_id")
    private String synsetId;

    @JsonProperty("definition")
    private String definition;

    @JsonProperty("pos")
    private String pos;

    @JsonProperty("score")
    private double score;

    @JsonProperty("rank")
    private int rank;

    @JsonProperty("relations")
    private RelationsDto relations;

    public CandidateSenseDto() {
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getSynsetId() {
        return synsetId;
    }

    public void setSynsetId(String synsetId) {
        this.synsetId = synsetId;
    }

    public String getDefinition() {
        return definition;
    }

    public void setDefinition(String definition) {
        this.definition = definition;
    }

    public String getPos() {
        return pos;
    }

    public void setPos(String pos) {
        this.pos = pos;
    }

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }

    public int getRank() {
        return rank;
    }

    public void setRank(int rank) {
        this.rank = rank;
    }

    public RelationsDto getRelations() {
        return relations != null ? relations : new RelationsDto();
    }

    public void setRelations(RelationsDto relations) {
        this.relations = relations;
    }
}

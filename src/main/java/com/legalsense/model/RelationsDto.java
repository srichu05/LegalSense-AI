package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

/**
 * WordNet lexical relations for a candidate sense.
 */
public class RelationsDto {

    @JsonProperty("synonyms")
    private List<String> synonyms = new ArrayList<>();

    @JsonProperty("hypernyms")
    private List<String> hypernyms = new ArrayList<>();

    @JsonProperty("hyponyms")
    private List<String> hyponyms = new ArrayList<>();

    public RelationsDto() {
    }

    public List<String> getSynonyms() {
        return synonyms != null ? synonyms : new ArrayList<>();
    }

    public void setSynonyms(List<String> synonyms) {
        this.synonyms = synonyms;
    }

    public List<String> getHypernyms() {
        return hypernyms != null ? hypernyms : new ArrayList<>();
    }

    public void setHypernyms(List<String> hypernyms) {
        this.hypernyms = hypernyms;
    }

    public List<String> getHyponyms() {
        return hyponyms != null ? hyponyms : new ArrayList<>();
    }

    public void setHyponyms(List<String> hyponyms) {
        this.hyponyms = hyponyms;
    }
}

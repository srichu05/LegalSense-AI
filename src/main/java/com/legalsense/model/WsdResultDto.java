package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

/**
 * Disambiguation result for a term occurrence.
 */
public class WsdResultDto {

    @JsonProperty("term")
    private String term;

    @JsonProperty("sentence")
    private String sentence;

    @JsonProperty("pos")
    private String pos;

    @JsonProperty("lemma")
    private String lemma;

    @JsonProperty("candidate_senses")
    private List<CandidateSenseDto> candidateSenses = new ArrayList<>();

    @JsonProperty("selected_sense")
    private CandidateSenseDto selectedSense;

    @JsonProperty("selection_method")
    private String selectionMethod;

    @JsonProperty("evidence")
    private List<EvidenceDto> evidence = new ArrayList<>();

    @JsonProperty("uncertain")
    private boolean uncertain;

    @JsonProperty("source_provenance")
    private List<String> sourceProvenance = new ArrayList<>();

    @JsonProperty("legal_glossary_entry")
    private GlossaryEntryDto legalGlossaryEntry;

    @JsonProperty("llm_assistance_status")
    private String llmAssistanceStatus;

    @JsonProperty("llm_suggested_sense")
    private String llmSuggestedSense;

    @JsonProperty("llm_rationale")
    private String llmRationale;

    // Optional document analysis fields
    @JsonProperty("page")
    private Integer page;

    @JsonProperty("passage_id")
    private String passageId;

    public WsdResultDto() {
    }

    public String getTerm() {
        return term;
    }

    public void setTerm(String term) {
        this.term = term;
    }

    public String getSentence() {
        return sentence;
    }

    public void setSentence(String sentence) {
        this.sentence = sentence;
    }

    public String getPos() {
        return pos;
    }

    public void setPos(String pos) {
        this.pos = pos;
    }

    public String getLemma() {
        return lemma;
    }

    public void setLemma(String lemma) {
        this.lemma = lemma;
    }

    public List<CandidateSenseDto> getCandidateSenses() {
        return candidateSenses != null ? candidateSenses : new ArrayList<>();
    }

    public void setCandidateSenses(List<CandidateSenseDto> candidateSenses) {
        this.candidateSenses = candidateSenses;
    }

    public CandidateSenseDto getSelectedSense() {
        return selectedSense;
    }

    public void setSelectedSense(CandidateSenseDto selectedSense) {
        this.selectedSense = selectedSense;
    }

    public String getSelectionMethod() {
        return selectionMethod;
    }

    public void setSelectionMethod(String selectionMethod) {
        this.selectionMethod = selectionMethod;
    }

    public List<EvidenceDto> getEvidence() {
        return evidence != null ? evidence : new ArrayList<>();
    }

    public void setEvidence(List<EvidenceDto> evidence) {
        this.evidence = evidence;
    }

    public boolean isUncertain() {
        return uncertain;
    }

    public void setUncertain(boolean uncertain) {
        this.uncertain = uncertain;
    }

    public List<String> getSourceProvenance() {
        return sourceProvenance != null ? sourceProvenance : new ArrayList<>();
    }

    public void setSourceProvenance(List<String> sourceProvenance) {
        this.sourceProvenance = sourceProvenance;
    }

    public GlossaryEntryDto getLegalGlossaryEntry() {
        return legalGlossaryEntry;
    }

    public void setLegalGlossaryEntry(GlossaryEntryDto legalGlossaryEntry) {
        this.legalGlossaryEntry = legalGlossaryEntry;
    }

    public String getLlmAssistanceStatus() {
        return llmAssistanceStatus;
    }

    public void setLlmAssistanceStatus(String llmAssistanceStatus) {
        this.llmAssistanceStatus = llmAssistanceStatus;
    }

    public String getLlmSuggestedSense() {
        return llmSuggestedSense;
    }

    public void setLlmSuggestedSense(String llmSuggestedSense) {
        this.llmSuggestedSense = llmSuggestedSense;
    }

    public String getLlmRationale() {
        return llmRationale;
    }

    public void setLlmRationale(String llmRationale) {
        this.llmRationale = llmRationale;
    }

    public Integer getPage() {
        return page;
    }

    public void setPage(Integer page) {
        this.page = page;
    }

    public String getPassageId() {
        return passageId;
    }

    public void setPassageId(String passageId) {
        this.passageId = passageId;
    }
}

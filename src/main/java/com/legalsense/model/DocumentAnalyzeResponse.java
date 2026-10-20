package com.legalsense.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

/**
 * Response payload for POST /api/v1/documents/analyze.
 */
public class DocumentAnalyzeResponse {

    @JsonProperty("request_id")
    private String requestId;

    @JsonProperty("document_id")
    private String documentId;

    @JsonProperty("filename")
    private String filename;

    @JsonProperty("file_type")
    private String fileType;

    @JsonProperty("character_count")
    private int characterCount;

    @JsonProperty("page_count")
    private int pageCount;

    @JsonProperty("passage_count")
    private int passageCount;

    @JsonProperty("occurrences_analyzed")
    private List<WsdResultDto> occurrencesAnalyzed = new ArrayList<>();

    @JsonProperty("warnings")
    private List<String> warnings = new ArrayList<>();

    public DocumentAnalyzeResponse() {
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public String getDocumentId() {
        return documentId;
    }

    public void setDocumentId(String documentId) {
        this.documentId = documentId;
    }

    public String getFilename() {
        return filename;
    }

    public void setFilename(String filename) {
        this.filename = filename;
    }

    public String getFileType() {
        return fileType;
    }

    public void setFileType(String fileType) {
        this.fileType = fileType;
    }

    public int getCharacterCount() {
        return characterCount;
    }

    public void setCharacterCount(int characterCount) {
        this.characterCount = characterCount;
    }

    public int getPageCount() {
        return pageCount;
    }

    public void setPageCount(int pageCount) {
        this.pageCount = pageCount;
    }

    public int getPassageCount() {
        return passageCount;
    }

    public void setPassageCount(int passageCount) {
        this.passageCount = passageCount;
    }

    public List<WsdResultDto> getOccurrencesAnalyzed() {
        return occurrencesAnalyzed != null ? occurrencesAnalyzed : new ArrayList<>();
    }

    public void setOccurrencesAnalyzed(List<WsdResultDto> occurrencesAnalyzed) {
        this.occurrencesAnalyzed = occurrencesAnalyzed;
    }

    public List<String> getWarnings() {
        return warnings != null ? warnings : new ArrayList<>();
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}

package com.legalsense.ui;

public enum ViewType {
    HOME("Home / Overview"),
    TEXT_ANALYSIS("Text Analysis"),
    DOCUMENT_ANALYSIS("Document Analysis"),
    CORPUS_SEARCH("Corpus Search"),
    SETTINGS("Settings");

    private final String title;

    ViewType(String title) {
        this.title = title;
    }

    public String getTitle() {
        return title;
    }
}

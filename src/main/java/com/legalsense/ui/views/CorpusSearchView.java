package com.legalsense.ui.views;

import com.legalsense.client.ApiClient;
import com.legalsense.client.ApiException;
import com.legalsense.model.SearchResponse;
import com.legalsense.model.SearchResultDto;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.*;

/**
 * Corpus Search workspace allowing users to perform TF-IDF and lexical queries
 * against bundled legal instruments, displaying scored passages and matched terms.
 */
public class CorpusSearchView extends ScrollPane {

    private final ApiClient apiClient;

    private final TextField queryField;
    private final Spinner<Integer> topKSpinner;
    private final Button searchBtn;
    private final Button clearBtn;
    private final ProgressIndicator progressIndicator;
    private final VBox warningContainer;
    private final VBox resultsContainer;

    public CorpusSearchView(ApiClient apiClient) {
        this.apiClient = apiClient;
        this.warningContainer = new VBox(8);
        this.resultsContainer = new VBox(12);

        setFitToWidth(true);
        setStyle("-fx-background-color: transparent; -fx-background: transparent;");

        VBox content = new VBox(16);
        content.setPadding(new Insets(20));
        content.setMaxWidth(960);

        // Section Title
        VBox titleBox = new VBox(4);
        Label title = new Label("Legal Corpus Search & Passage Retrieval");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold; -fx-text-fill: #0F172A;");
        Label subtitle = new Label("Retrieve relevant passages from indexed contracts and court rulings using TF-IDF, lexical matching, and legal glossary terms.");
        subtitle.setStyle("-fx-font-size: 12px; -fx-text-fill: #64748B;");
        titleBox.getChildren().addAll(title, subtitle);
        content.getChildren().add(titleBox);

        // Search Control Card
        VBox searchCard = new VBox(12);
        searchCard.getStyleClass().add("card");

        Label queryLabel = new Label("Search Query:");
        queryLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: #334155;");

        queryField = new TextField();
        queryField.setPromptText("Enter legal search terms (e.g. 'consideration exchanged under a contract')...");
        queryField.setOnAction(e -> runSearch());

        // Sample queries
        HBox sampleRow = new HBox(8);
        sampleRow.setAlignment(Pos.CENTER_LEFT);
        Label samplePrompt = new Label("Sample queries:");
        samplePrompt.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B;");

        Button sample1 = new Button("Contract consideration");
        sample1.getStyleClass().add("btn-secondary");
        sample1.setStyle("-fx-font-size: 11px; -fx-padding: 3px 8px;");
        sample1.setOnAction(e -> queryField.setText("consideration exchanged under a contract"));

        Button sample2 = new Button("Motion to dismiss");
        sample2.getStyleClass().add("btn-secondary");
        sample2.setStyle("-fx-font-size: 11px; -fx-padding: 3px 8px;");
        sample2.setOnAction(e -> queryField.setText("motion for summary judgment or dismissal"));

        Button sample3 = new Button("Confidentiality obligations");
        sample3.getStyleClass().add("btn-secondary");
        sample3.setStyle("-fx-font-size: 11px; -fx-padding: 3px 8px;");
        sample3.setOnAction(e -> queryField.setText("confidentiality proprietary information disclosure"));

        sampleRow.getChildren().addAll(samplePrompt, sample1, sample2, sample3);

        // Actions and controls row
        HBox actionRow = new HBox(16);
        actionRow.setAlignment(Pos.CENTER_LEFT);

        Label topKLabel = new Label("Max Results (top_k):");
        topKLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #475569;");
        topKSpinner = new Spinner<>(1, 20, 5);
        topKSpinner.setPrefWidth(75);

        searchBtn = new Button("Search Corpus");
        searchBtn.getStyleClass().add("btn-primary");
        searchBtn.setOnAction(e -> runSearch());

        clearBtn = new Button("Clear");
        clearBtn.getStyleClass().add("btn-secondary");
        clearBtn.setOnAction(e -> {
            queryField.clear();
            warningContainer.getChildren().clear();
            showEmptyResults();
        });

        progressIndicator = new ProgressIndicator();
        progressIndicator.setPrefSize(22, 22);
        progressIndicator.setVisible(false);

        actionRow.getChildren().addAll(searchBtn, clearBtn, topKLabel, topKSpinner, progressIndicator);

        // Score interpretation notice
        Label noticeLabel = new Label("ℹ Note: Retrieval score is a ranking signal derived from TF-IDF and term overlap; it is not a statistical probability of legal validity.");
        noticeLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B; -fx-font-style: italic;");

        searchCard.getChildren().addAll(queryLabel, queryField, sampleRow, actionRow, noticeLabel);
        content.getChildren().add(searchCard);

        // Warnings & Results containers
        content.getChildren().add(warningContainer);
        content.getChildren().add(resultsContainer);

        showEmptyResults();
        setContent(content);
    }

    private void runSearch() {
        String query = queryField.getText();
        if (query == null || query.isBlank()) {
            showError("Query Error", "Please enter a search query.");
            return;
        }

        int topK = topKSpinner.getValue();

        setLoading(true);
        warningContainer.getChildren().clear();
        resultsContainer.getChildren().clear();

        apiClient.searchCorpus(query, topK)
                .whenComplete((response, ex) -> {
                    Platform.runLater(() -> {
                        setLoading(false);
                        if (ex != null) {
                            handleError(ex);
                        } else {
                            renderSearchResults(response);
                        }
                    });
                });
    }

    private void renderSearchResults(SearchResponse response) {
        if (response == null || response.getResults() == null || response.getResults().isEmpty()) {
            Label noRes = new Label("No matching passages found for: \"" + response.getQuery() + "\"");
            noRes.setStyle("-fx-font-size: 13px; -fx-text-fill: #64748B; -fx-font-style: italic; -fx-padding: 20px;");
            resultsContainer.getChildren().add(noRes);
            return;
        }

        // Warnings
        if (response.getWarnings() != null && !response.getWarnings().isEmpty()) {
            for (String w : response.getWarnings()) {
                Label warn = new Label("Notice: " + w);
                warn.getStyleClass().add("banner-warning");
                warn.setMaxWidth(Double.MAX_VALUE);
                warningContainer.getChildren().add(warn);
            }
        }

        // Header
        Label countLabel = new Label("Search Hits (" + response.getResults().size() + " passages):");
        countLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: #0F172A; -fx-font-size: 14px;");
        resultsContainer.getChildren().add(countLabel);

        int rank = 1;
        for (SearchResultDto hit : response.getResults()) {
            VBox hitCard = new VBox(8);
            hitCard.getStyleClass().add("card");

            HBox topRow = new HBox(8);
            topRow.setAlignment(Pos.CENTER_LEFT);

            Label rankBadge = new Label("#" + rank++);
            rankBadge.setStyle("-fx-font-weight: bold; -fx-text-fill: #475569;");

            Label docBadge = new Label(hit.getDocumentName() != null ? hit.getDocumentName() : "Bundled Document");
            docBadge.getStyleClass().add("badge-wordnet");

            if (hit.getPage() != null) {
                Label pageBadge = new Label("Page " + hit.getPage());
                pageBadge.setStyle("-fx-background-color: #E0E7FF; -fx-text-fill: #3730A3; -fx-padding: 3px 8px; -fx-background-radius: 4px; -fx-font-size: 11px;");
                topRow.getChildren().add(pageBadge);
            }

            Region spacer = new Region();
            HBox.setHgrow(spacer, Priority.ALWAYS);

            Label scoreBadge = new Label(String.format("Score: %.4f", hit.getScore()));
            scoreBadge.setStyle("-fx-background-color: #FEF3C7; -fx-text-fill: #92400E; -fx-padding: 3px 8px; -fx-background-radius: 4px; -fx-font-weight: bold; -fx-font-size: 11px;");

            topRow.getChildren().addAll(rankBadge, docBadge, spacer, scoreBadge);
            hitCard.getChildren().add(topRow);

            // Passage Excerpt
            Label passageText = new Label(hit.getPassage());
            passageText.setWrapText(true);
            passageText.setStyle("-fx-font-size: 13px; -fx-text-fill: #1E293B; -fx-line-spacing: 2px; -fx-background-color: #F8FAFC; -fx-padding: 10px; -fx-border-color: #E2E8F0; -fx-border-width: 1px; -fx-border-radius: 4px; -fx-background-radius: 4px;");
            hitCard.getChildren().add(passageText);

            // Matched terms
            if (hit.getMatchedTerms() != null && !hit.getMatchedTerms().isEmpty()) {
                HBox termsRow = new HBox(6);
                termsRow.setAlignment(Pos.CENTER_LEFT);
                Label matchedLabel = new Label("Matched Terms:");
                matchedLabel.setStyle("-fx-font-size: 11px; -fx-font-weight: bold; -fx-text-fill: #64748B;");
                termsRow.getChildren().add(matchedLabel);

                for (String term : hit.getMatchedTerms()) {
                    Label termPill = new Label(term);
                    termPill.setStyle("-fx-background-color: #E2E8F0; -fx-text-fill: #334155; -fx-padding: 2px 6px; -fx-background-radius: 3px; -fx-font-size: 10px; -fx-font-weight: bold;");
                    termsRow.getChildren().add(termPill);
                }
                hitCard.getChildren().add(termsRow);
            }

            resultsContainer.getChildren().add(hitCard);
        }
    }

    private void handleError(Throwable ex) {
        Throwable cause = ex.getCause() != null ? ex.getCause() : ex;
        String message = cause.getMessage();

        if (cause instanceof ApiException apiEx) {
            message = apiEx.getUserFacingMessage();
        }

        showError("Search Error", message);
    }

    private void showError(String title, String message) {
        VBox errBox = new VBox(6);
        errBox.setStyle("-fx-background-color: #FEF2F2; -fx-border-color: #F87171; -fx-border-width: 1px; -fx-border-radius: 6px; -fx-padding: 12px;");

        Label errTitle = new Label(title);
        errTitle.setStyle("-fx-font-weight: bold; -fx-text-fill: #991B1B;");

        Label errText = new Label(message);
        errText.setWrapText(true);
        errText.setStyle("-fx-text-fill: #B91C1C;");

        errBox.getChildren().addAll(errTitle, errText);
        warningContainer.getChildren().add(errBox);
    }

    private void showEmptyResults() {
        resultsContainer.getChildren().clear();
        VBox emptyBox = new VBox(8);
        emptyBox.setAlignment(Pos.CENTER);
        emptyBox.setPadding(new Insets(40, 20, 40, 20));

        Label emptyTitle = new Label("Ready to Search Corpus");
        emptyTitle.setStyle("-fx-font-size: 15px; -fx-font-weight: bold; -fx-text-fill: #64748B;");

        Label emptySubtitle = new Label("Enter legal concepts above or select a sample query to retrieve ranked passages.");
        emptySubtitle.setStyle("-fx-font-size: 12px; -fx-text-fill: #94A3B8;");

        emptyBox.getChildren().addAll(emptyTitle, emptySubtitle);
        resultsContainer.getChildren().add(emptyBox);
    }

    private void setLoading(boolean loading) {
        progressIndicator.setVisible(loading);
        searchBtn.setDisable(loading);
        queryField.setDisable(loading);
        topKSpinner.setDisable(loading);
    }
}

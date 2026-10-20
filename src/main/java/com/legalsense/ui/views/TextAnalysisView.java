package com.legalsense.ui.views;

import com.legalsense.client.ApiClient;
import com.legalsense.client.ApiException;
import com.legalsense.model.AnalyzeResponse;
import com.legalsense.model.WsdResultDto;
import com.legalsense.ui.components.SenseDetailCard;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.*;

/**
 * Text Analysis workspace allowing users to input legal clauses or sentences,
 * specify target terms, trigger WSD analysis asynchronously, and inspect
 * WordNet rankings, evidence, and legal glossary entries.
 */
public class TextAnalysisView extends ScrollPane {

    private final ApiClient apiClient;

    private final TextArea inputArea;
    private final TextField targetWordField;
    private final CheckBox useLlmCheckBox;
    private final Button analyzeButton;
    private final Button clearButton;
    private final ProgressIndicator progressIndicator;
    private final VBox resultsContainer;
    private final VBox warningContainer;

    public TextAnalysisView(ApiClient apiClient) {
        this.apiClient = apiClient;
        this.inputArea = new TextArea();
        this.targetWordField = new TextField();
        this.useLlmCheckBox = new CheckBox("Request Groq LLM assistance (if enabled on backend)");
        this.analyzeButton = new Button("Run Analysis");
        this.clearButton = new Button("Clear");
        this.progressIndicator = new ProgressIndicator();
        this.warningContainer = new VBox(8);
        this.resultsContainer = new VBox(16);

        setFitToWidth(true);
        setStyle("-fx-background-color: transparent; -fx-background: transparent;");

        VBox content = new VBox(16);
        content.setPadding(new Insets(20));
        content.setMaxWidth(960);

        // Section Title
        VBox titleBox = new VBox(4);
        Label title = new Label("Text Analysis & Word Sense Disambiguation");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold; -fx-text-fill: #0F172A;");
        Label subtitle = new Label("Disambiguate polysemous legal terms within sentences or contractual clauses using Extended Lesk & curated glossary.");
        subtitle.setStyle("-fx-font-size: 12px; -fx-text-fill: #64748B;");
        titleBox.getChildren().addAll(title, subtitle);
        content.getChildren().add(titleBox);

        // Input Card
        VBox inputCard = new VBox(12);
        inputCard.getStyleClass().add("card");

        Label inputLabel = new Label("Legal Text / Clause (up to 50,000 characters):");
        inputLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: #334155;");

        inputArea.setPromptText("Enter legal text here (e.g. 'The parties provided adequate consideration under the instrument.')...");
        inputArea.setWrapText(true);
        inputArea.setPrefRowCount(4);

        // Sample buttons row
        HBox sampleRow = new HBox(10);
        sampleRow.setAlignment(Pos.CENTER_LEFT);
        Label samplePrompt = new Label("Load sample:");
        samplePrompt.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B;");

        Button sample1 = new Button("Contract Consideration");
        sample1.getStyleClass().add("btn-secondary");
        sample1.setStyle("-fx-font-size: 11px; -fx-padding: 4px 8px;");
        sample1.setOnAction(e -> {
            inputArea.setText("The buyer provided adequate consideration by transferring marketable title to the real property.");
            targetWordField.setText("consideration");
        });

        Button sample2 = new Button("Motion Excerpt");
        sample2.getStyleClass().add("btn-secondary");
        sample2.setStyle("-fx-font-size: 11px; -fx-padding: 4px 8px;");
        sample2.setOnAction(e -> {
            inputArea.setText("Counsel filed an urgent motion for summary judgment requesting expedited dismissal of all claims.");
            targetWordField.setText("motion");
        });

        Button sample3 = new Button("Instrument Execution");
        sample3.getStyleClass().add("btn-secondary");
        sample3.setStyle("-fx-font-size: 11px; -fx-padding: 4px 8px;");
        sample3.setOnAction(e -> {
            inputArea.setText("The commercial lease instrument was duly executed in counterpart by both authorized representatives.");
            targetWordField.setText("instrument");
        });

        sampleRow.getChildren().addAll(samplePrompt, sample1, sample2, sample3);

        // Target word & options row
        HBox optionsRow = new HBox(16);
        optionsRow.setAlignment(Pos.CENTER_LEFT);

        VBox targetBox = new VBox(4);
        Label targetLabel = new Label("Target Term (Optional):");
        targetWordField.setPromptText("e.g. consideration (leave empty for auto-detect)");
        targetWordField.setPrefWidth(300);
        targetBox.getChildren().addAll(targetLabel, targetWordField);

        useLlmCheckBox.setStyle("-fx-font-size: 12px; -fx-text-fill: #334155; -fx-padding: 16px 0 0 0;");

        optionsRow.getChildren().addAll(targetBox, useLlmCheckBox);

        // Action Buttons Row
        HBox actionRow = new HBox(12);
        actionRow.setAlignment(Pos.CENTER_LEFT);

        analyzeButton.getStyleClass().add("btn-primary");
        analyzeButton.setOnAction(e -> runAnalysis());

        clearButton.getStyleClass().add("btn-secondary");
        clearButton.setOnAction(e -> {
            inputArea.clear();
            targetWordField.clear();
            warningContainer.getChildren().clear();
            showEmptyResults();
        });

        progressIndicator.setPrefSize(22, 22);
        progressIndicator.setVisible(false);

        actionRow.getChildren().addAll(analyzeButton, clearButton, progressIndicator);

        inputCard.getChildren().addAll(inputLabel, inputArea, sampleRow, optionsRow, actionRow);
        content.getChildren().add(inputCard);

        // Warning & Results Containers
        content.getChildren().add(warningContainer);
        content.getChildren().add(resultsContainer);

        showEmptyResults();
        setContent(content);
    }

    private void runAnalysis() {
        String text = inputArea.getText();
        if (text == null || text.isBlank()) {
            showError("Input Error", "Please enter legal text or select a sample clause to analyze.");
            return;
        }

        String targetWord = targetWordField.getText();
        boolean useLlm = useLlmCheckBox.isSelected();

        setLoading(true);
        warningContainer.getChildren().clear();
        resultsContainer.getChildren().clear();

        apiClient.analyzeText(text, targetWord, useLlm)
                .whenComplete((response, ex) -> {
                    Platform.runLater(() -> {
                        setLoading(false);
                        if (ex != null) {
                            handleAnalysisError(ex);
                        } else {
                            renderAnalysisResults(response);
                        }
                    });
                });
    }

    private void renderAnalysisResults(AnalyzeResponse response) {
        if (response == null || response.getResults() == null || response.getResults().isEmpty()) {
            Label noRes = new Label("No candidate terms or WordNet senses were detected in the provided text.");
            noRes.setStyle("-fx-font-size: 13px; -fx-text-fill: #64748B; -fx-font-style: italic; -fx-padding: 20px;");
            resultsContainer.getChildren().add(noRes);
            return;
        }

        // Display any backend warnings
        if (response.getWarnings() != null && !response.getWarnings().isEmpty()) {
            for (String w : response.getWarnings()) {
                Label warnLabel = new Label("Notice: " + w);
                warnLabel.getStyleClass().add("banner-warning");
                warnLabel.setMaxWidth(Double.MAX_VALUE);
                warningContainer.getChildren().add(warnLabel);
            }
        }

        // Summary bar
        HBox summaryBar = new HBox(12);
        summaryBar.setAlignment(Pos.CENTER_LEFT);
        summaryBar.setStyle("-fx-padding: 4px 0;");

        Label countLabel = new Label("Analyzed Term Results (" + response.getResults().size() + "):");
        countLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: #0F172A; -fx-font-size: 14px;");

        Label reqIdLabel = new Label("Request ID: " + response.getRequestId());
        reqIdLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #94A3B8;");

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        summaryBar.getChildren().addAll(countLabel, spacer, reqIdLabel);
        resultsContainer.getChildren().add(summaryBar);

        // Render each term result
        for (WsdResultDto result : response.getResults()) {
            SenseDetailCard card = new SenseDetailCard(result);
            resultsContainer.getChildren().add(card);
        }
    }

    private void handleAnalysisError(Throwable ex) {
        Throwable cause = ex.getCause() != null ? ex.getCause() : ex;
        String message = cause.getMessage();

        if (cause instanceof ApiException apiEx) {
            message = apiEx.getUserFacingMessage();
        }

        showError("Analysis Failed", message);
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

        Label emptyTitle = new Label("Ready to Analyze Legal Text");
        emptyTitle.setStyle("-fx-font-size: 15px; -fx-font-weight: bold; -fx-text-fill: #64748B;");

        Label emptySubtitle = new Label("Paste legal text above or click one of the sample buttons, then click 'Run Analysis'.");
        emptySubtitle.setStyle("-fx-font-size: 12px; -fx-text-fill: #94A3B8;");

        emptyBox.getChildren().addAll(emptyTitle, emptySubtitle);
        resultsContainer.getChildren().add(emptyBox);
    }

    private void setLoading(boolean loading) {
        progressIndicator.setVisible(loading);
        analyzeButton.setDisable(loading);
        clearButton.setDisable(loading);
        inputArea.setDisable(loading);
        targetWordField.setDisable(loading);
    }
}

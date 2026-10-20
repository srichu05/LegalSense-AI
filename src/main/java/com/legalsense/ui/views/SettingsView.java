package com.legalsense.ui.views;

import com.legalsense.client.ApiClient;
import com.legalsense.model.HealthResponse;
import com.legalsense.ui.components.ConnectionStatusBadge;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.*;

import java.net.URI;

/**
 * Settings workspace allowing configuration of the Flask backend base URL,
 * executing health checks, and validating server capabilities without exposing secrets.
 */
public class SettingsView extends ScrollPane {

    private final ApiClient apiClient;
    private final ConnectionStatusBadge globalStatusBadge;

    private final TextField urlField;
    private final Button testBtn;
    private final Button saveBtn;
    private final Button resetBtn;
    private final ProgressIndicator progressIndicator;
    private final VBox feedbackContainer;

    public SettingsView(ApiClient apiClient, ConnectionStatusBadge globalStatusBadge) {
        this.apiClient = apiClient;
        this.globalStatusBadge = globalStatusBadge;
        setFitToWidth(true);
        setStyle("-fx-background-color: transparent; -fx-background: transparent;");

        VBox content = new VBox(16);
        content.setPadding(new Insets(20));
        content.setMaxWidth(800);

        // Section Title
        VBox titleBox = new VBox(4);
        Label title = new Label("Settings & API Connection");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold; -fx-text-fill: #0F172A;");
        Label subtitle = new Label("Configure the LegalSense Python Flask REST backend endpoint and test connectivity.");
        subtitle.setStyle("-fx-font-size: 12px; -fx-text-fill: #64748B;");
        titleBox.getChildren().addAll(title, subtitle);
        content.getChildren().add(titleBox);

        // Connection Card
        VBox connCard = new VBox(12);
        connCard.getStyleClass().add("card");

        Label endpointHeader = new Label("Backend Service Base URL");
        endpointHeader.setStyle("-fx-font-weight: bold; -fx-text-fill: #334155;");

        urlField = new TextField(apiClient.getBaseUrl());
        urlField.setPromptText("http://127.0.0.1:5000");

        HBox btnRow = new HBox(10);
        btnRow.setAlignment(Pos.CENTER_LEFT);

        testBtn = new Button("Test Connection");
        testBtn.getStyleClass().add("btn-secondary");
        testBtn.setOnAction(e -> testConnection(urlField.getText()));

        saveBtn = new Button("Save & Apply");
        saveBtn.getStyleClass().add("btn-primary");
        saveBtn.setOnAction(e -> saveBaseUrl(urlField.getText()));

        resetBtn = new Button("Reset to Default");
        resetBtn.getStyleClass().add("btn-secondary");
        resetBtn.setOnAction(e -> {
            urlField.setText(ApiClient.DEFAULT_BASE_URL);
            saveBaseUrl(ApiClient.DEFAULT_BASE_URL);
        });

        progressIndicator = new ProgressIndicator();
        progressIndicator.setPrefSize(20, 20);
        progressIndicator.setVisible(false);

        btnRow.getChildren().addAll(saveBtn, testBtn, resetBtn, progressIndicator);

        Label helpText = new Label("Default local development endpoint is http://127.0.0.1:5000. Changes apply immediately to all active workspaces.");
        helpText.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B;");

        connCard.getChildren().addAll(endpointHeader, urlField, btnRow, helpText);
        content.getChildren().add(connCard);

        // Feedback / Health Details Container
        feedbackContainer = new VBox(10);
        content.getChildren().add(feedbackContainer);

        // Security & Architectural Boundary Card
        VBox secCard = new VBox(8);
        secCard.getStyleClass().add("card");
        secCard.setStyle("-fx-background-color: #F8FAFC; -fx-border-color: #E2E8F0;");

        Label secTitle = new Label("Security & Secret Boundary Policy");
        secTitle.setStyle("-fx-font-size: 13px; -fx-font-weight: bold; -fx-text-fill: #334155;");

        Label secDesc = new Label(
                "• No API keys, database credentials, or secret tokens are managed or stored in the Java desktop client.\n" +
                "• Groq LLM API keys belong exclusively in the backend server environment (.env) and are never transmitted over the wire.\n" +
                "• Document uploads are processed in-memory by the backend without persistent disk storage.\n" +
                "• Health checks inspect only operational readiness (WSD readiness and whether LLM assistance is configured)."
        );
        secDesc.setStyle("-fx-font-size: 12px; -fx-text-fill: #64748B; -fx-line-spacing: 3px;");

        secCard.getChildren().addAll(secTitle, secDesc);
        content.getChildren().add(secCard);

        setContent(content);
    }

    private void saveBaseUrl(String input) {
        if (!validateUrl(input)) return;

        apiClient.setBaseUrl(input.trim());
        globalStatusBadge.refreshStatus(apiClient);

        showSuccess("Base URL Updated", "Active backend endpoint is now set to: " + apiClient.getBaseUrl());
    }

    private void testConnection(String input) {
        if (!validateUrl(input)) return;

        String testUrl = input.trim();
        ApiClient tempClient = new ApiClient(testUrl);

        setLoading(true);
        feedbackContainer.getChildren().clear();

        long startTime = System.currentTimeMillis();
        tempClient.checkHealth().whenComplete((health, ex) -> {
            long latency = System.currentTimeMillis() - startTime;
            Platform.runLater(() -> {
                setLoading(false);
                if (ex != null || health == null || !health.isHealthy()) {
                    String msg = ex != null ? ex.getMessage() : "Backend returned an unexpected health status.";
                    showError("Connection Failed", "Unable to establish communication with " + testUrl + ":\n" + msg);
                } else {
                    renderHealthDetails(health, testUrl, latency);
                }
            });
        });
    }

    private boolean validateUrl(String url) {
        if (url == null || url.isBlank()) {
            showError("Invalid URL", "Base URL cannot be empty.");
            return false;
        }
        try {
            URI u = URI.create(url.trim());
            if (u.getScheme() == null || (!u.getScheme().equalsIgnoreCase("http") && !u.getScheme().equalsIgnoreCase("https"))) {
                showError("Invalid URL", "URL must start with http:// or https://");
                return false;
            }
        } catch (Exception e) {
            showError("Invalid URL", "Malformed URL syntax: " + e.getMessage());
            return false;
        }
        return true;
    }

    private void renderHealthDetails(HealthResponse health, String url, long latencyMs) {
        VBox card = new VBox(10);
        card.getStyleClass().add("card");
        card.setStyle("-fx-background-color: #F0FDF4; -fx-border-color: #86EFAC; -fx-border-width: 1.5px;");

        HBox top = new HBox(8);
        top.setAlignment(Pos.CENTER_LEFT);
        Label badge = new Label("✓ BACKEND CONNECTED");
        badge.setStyle("-fx-background-color: #DCFCE7; -fx-text-fill: #15803D; -fx-font-weight: bold; -fx-padding: 3px 8px; -fx-background-radius: 4px;");

        Label latencyLabel = new Label("Response time: " + latencyMs + " ms");
        latencyLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #166534;");
        top.getChildren().addAll(badge, latencyLabel);

        Label serviceLabel = new Label("Service: " + health.getService() + " | Status: " + health.getStatus());
        serviceLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: #14532D;");

        Label wsdLabel = new Label("WordNet & WSD Readiness: " + (health.isWsdReady() ? "Ready (WordNet corpora loaded)" : "Not ready"));
        wsdLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #166534;");

        Label llmLabel = new Label("Groq LLM Assistance: " + (health.isLlmEnabled() ? "Enabled (Server GROQ_API_KEY present)" : "Disabled (Local WSD only)"));
        llmLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #166534;");

        card.getChildren().addAll(top, serviceLabel, wsdLabel, llmLabel);
        feedbackContainer.getChildren().setAll(card);
    }

    private void showError(String title, String message) {
        VBox box = new VBox(6);
        box.setStyle("-fx-background-color: #FEF2F2; -fx-border-color: #F87171; -fx-border-width: 1px; -fx-border-radius: 6px; -fx-padding: 12px;");

        Label t = new Label(title);
        t.setStyle("-fx-font-weight: bold; -fx-text-fill: #991B1B;");

        Label m = new Label(message);
        m.setWrapText(true);
        m.setStyle("-fx-text-fill: #B91C1C;");

        box.getChildren().addAll(t, m);
        feedbackContainer.getChildren().setAll(box);
    }

    private void showSuccess(String title, String message) {
        VBox box = new VBox(6);
        box.setStyle("-fx-background-color: #F0FDF4; -fx-border-color: #86EFAC; -fx-border-width: 1px; -fx-border-radius: 6px; -fx-padding: 12px;");

        Label t = new Label(title);
        t.setStyle("-fx-font-weight: bold; -fx-text-fill: #15803D;");

        Label m = new Label(message);
        m.setWrapText(true);
        m.setStyle("-fx-text-fill: #166534;");

        box.getChildren().addAll(t, m);
        feedbackContainer.getChildren().setAll(box);
    }

    private void setLoading(boolean loading) {
        progressIndicator.setVisible(loading);
        testBtn.setDisable(loading);
        saveBtn.setDisable(loading);
        resetBtn.setDisable(loading);
    }
}

package com.legalsense.ui.views;

import com.legalsense.client.ApiClient;
import com.legalsense.ui.ViewType;
import com.legalsense.ui.components.ConnectionStatusBadge;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.*;

import java.util.function.Consumer;

/**
 * Home / Overview view providing project context, backend connectivity status,
 * and entry points to core functionality without fabricated statistics.
 */
public class HomeView extends ScrollPane {

    public HomeView(ApiClient apiClient, ConnectionStatusBadge statusBadge, Consumer<ViewType> navigationHandler) {
        setFitToWidth(true);
        setStyle("-fx-background-color: transparent; -fx-background: transparent;");

        VBox content = new VBox(20);
        content.setPadding(new Insets(24));
        content.setMaxWidth(960);
        content.setAlignment(Pos.TOP_LEFT);

        // Header / Welcome Card
        VBox heroCard = new VBox(10);
        heroCard.getStyleClass().add("card");
        heroCard.setStyle("-fx-background-color: linear-gradient(to right, #0F172A, #1E293B); -fx-background-radius: 8px; -fx-padding: 24px;");

        Label title = new Label("LegalSense");
        title.setStyle("-fx-font-size: 26px; -fx-font-weight: bold; -fx-text-fill: #FFFFFF;");

        Label subtitle = new Label("Context-Aware Legal Document Analysis & Word Sense Disambiguation");
        subtitle.setStyle("-fx-font-size: 14px; -fx-text-fill: #94A3B8;");

        Label description = new Label(
                "LegalSense resolves semantic ambiguity in legal instruments by combining WordNet lexical relations, " +
                "an Extended Lesk disambiguation engine, and an authoritative curated legal glossary. " +
                "Designed for legal research, contract review, and computational linguistics evaluation."
        );
        description.setWrapText(true);
        description.setStyle("-fx-font-size: 13px; -fx-text-fill: #CBD5E1; -fx-padding: 8px 0 0 0;");

        heroCard.getChildren().addAll(title, subtitle, description);
        content.getChildren().add(heroCard);

        // Backend Status Card
        VBox statusCard = new VBox(12);
        statusCard.getStyleClass().add("card");

        HBox statusTop = new HBox(12);
        statusTop.setAlignment(Pos.CENTER_LEFT);

        Label statusHeader = new Label("Backend Connection Status");
        statusHeader.getStyleClass().add("card-title");

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        Button testConnBtn = new Button("Refresh Connection");
        testConnBtn.getStyleClass().add("btn-secondary");
        testConnBtn.setOnAction(e -> statusBadge.refreshStatus(apiClient));

        Button configBtn = new Button("Configure Settings");
        configBtn.getStyleClass().add("btn-secondary");
        configBtn.setOnAction(e -> navigationHandler.accept(ViewType.SETTINGS));

        statusTop.getChildren().addAll(statusHeader, spacer, testConnBtn, configBtn);

        HBox statusDetails = new HBox(16);
        statusDetails.setAlignment(Pos.CENTER_LEFT);

        Label endpointLabel = new Label("Active Endpoint: " + apiClient.getBaseUrl());
        endpointLabel.setStyle("-fx-font-family: monospace; -fx-text-fill: #475569;");

        statusDetails.getChildren().addAll(endpointLabel);

        statusCard.getChildren().addAll(statusTop, statusDetails);
        content.getChildren().add(statusCard);

        // Section: Primary Workspaces
        Label sectionTitle = new Label("Workspaces & Core Tools");
        sectionTitle.setStyle("-fx-font-size: 16px; -fx-font-weight: bold; -fx-text-fill: #1E293B; -fx-padding: 8px 0 0 0;");
        content.getChildren().add(sectionTitle);

        GridPane grid = new GridPane();
        grid.setHgap(16);
        grid.setVgap(16);

        ColumnConstraints col1 = new ColumnConstraints();
        col1.setPercentWidth(33.33);
        ColumnConstraints col2 = new ColumnConstraints();
        col2.setPercentWidth(33.33);
        ColumnConstraints col3 = new ColumnConstraints();
        col3.setPercentWidth(33.33);
        grid.getColumnConstraints().addAll(col1, col2, col3);

        // Card 1: Text Analysis
        VBox card1 = createFeatureCard(
                "Text Analysis",
                "Disambiguate ambiguous legal terms within clauses or sentences. View WordNet senses, definitions, Lesk scores, and legal glossary entries.",
                "Open Text Analysis",
                () -> navigationHandler.accept(ViewType.TEXT_ANALYSIS)
        );
        grid.add(card1, 0, 0);

        // Card 2: Document Analysis
        VBox card2 = createFeatureCard(
                "Document Analysis",
                "Ingest plain text (.txt) and PDF (.pdf) legal documents. Automatic sentence segmentation, glossary occurrence scanning, and metadata reporting.",
                "Open Document Analysis",
                () -> navigationHandler.accept(ViewType.DOCUMENT_ANALYSIS)
        );
        grid.add(card2, 1, 0);

        // Card 3: Corpus Search
        VBox card3 = createFeatureCard(
                "Corpus Search",
                "Execute lexical and TF-IDF search queries against indexed legal ruling and contract corpora with passage-level scoring.",
                "Open Corpus Search",
                () -> navigationHandler.accept(ViewType.CORPUS_SEARCH)
        );
        grid.add(card3, 2, 0);

        content.getChildren().add(grid);

        // Notice / Academic Scope Panel
        VBox scopeCard = new VBox(6);
        scopeCard.getStyleClass().add("card");
        scopeCard.setStyle("-fx-background-color: #F8FAFC; -fx-border-color: #E2E8F0;");

        Label scopeTitle = new Label("System Architectural Principles & Scope");
        scopeTitle.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #475569;");

        Label scopeDesc = new Label(
                "• Explicit Separation: WordNet lexical senses and curated legal definitions are maintained as distinct knowledge sources.\n" +
                "• Transparent Evidence: Every ranking exposes exact token overlap contributions and candidate relations (hypernyms, hyponyms).\n" +
                "• Uncertainty Awareness: Low-confidence results and score ties are visibly flagged without overstating certainty.\n" +
                "• Secure Integration: All NLP processing is executed on the Python backend; client communicates strictly via structured REST JSON."
        );
        scopeDesc.setStyle("-fx-font-size: 12px; -fx-text-fill: #64748B; -fx-line-spacing: 3px;");

        scopeCard.getChildren().addAll(scopeTitle, scopeDesc);
        content.getChildren().add(scopeCard);

        setContent(content);
    }

    private VBox createFeatureCard(String title, String desc, String btnText, Runnable action) {
        VBox card = new VBox(10);
        card.getStyleClass().add("card");
        VBox.setVgrow(card, Priority.ALWAYS);

        Label cardTitle = new Label(title);
        cardTitle.getStyleClass().add("card-title");

        Label cardDesc = new Label(desc);
        cardDesc.setWrapText(true);
        cardDesc.getStyleClass().add("card-subtitle");
        cardDesc.setMinHeight(75);

        Region spacer = new Region();
        VBox.setVgrow(spacer, Priority.ALWAYS);

        Button btn = new Button(btnText);
        btn.getStyleClass().add("btn-primary");
        btn.setMaxWidth(Double.MAX_VALUE);
        btn.setOnAction(e -> action.run());

        card.getChildren().addAll(cardTitle, cardDesc, spacer, btn);
        return card;
    }
}

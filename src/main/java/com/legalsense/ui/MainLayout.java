package com.legalsense.ui;

import com.legalsense.client.ApiClient;
import com.legalsense.ui.components.ConnectionStatusBadge;
import com.legalsense.ui.components.DisclaimerBanner;
import com.legalsense.ui.views.*;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.*;

import java.util.EnumMap;
import java.util.Map;

/**
 * Root application layout managing navigation, active views, connection badges,
 * and academic disclaimer banner.
 */
public class MainLayout extends BorderPane {

    private final ApiClient apiClient;
    private final ConnectionStatusBadge statusBadge;
    private final Map<ViewType, Button> navButtons = new EnumMap<>(ViewType.class);
    private final Map<ViewType, Node> viewCache = new EnumMap<>(ViewType.class);
    private ViewType currentView;

    public MainLayout(ApiClient apiClient) {
        this.apiClient = apiClient;
        this.statusBadge = new ConnectionStatusBadge();

        setTop(createHeader());
        setBottom(new DisclaimerBanner());

        // Default to Home view
        navigateTo(ViewType.HOME);

        // Initial health check
        statusBadge.refreshStatus(apiClient);
    }

    private Node createHeader() {
        HBox header = new HBox(16);
        header.getStyleClass().add("header-bar");
        header.setAlignment(Pos.CENTER_LEFT);

        // Brand section
        VBox brandBox = new VBox(2);
        Label brandTitle = new Label("⚖ LegalSense");
        brandTitle.getStyleClass().add("brand-title");

        Label brandSubtitle = new Label("Legal NLP & Word Sense Disambiguation");
        brandSubtitle.getStyleClass().add("brand-subtitle");

        brandBox.getChildren().addAll(brandTitle, brandSubtitle);
        header.getChildren().add(brandBox);

        // Navigation buttons
        HBox navBox = new HBox(6);
        navBox.setAlignment(Pos.CENTER_LEFT);

        for (ViewType vt : ViewType.values()) {
            Button btn = new Button(vt.getTitle());
            btn.getStyleClass().add("nav-btn");
            btn.setOnAction(e -> navigateTo(vt));
            navButtons.put(vt, btn);
            navBox.getChildren().add(btn);
        }

        header.getChildren().add(navBox);

        // Spacer
        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);
        header.getChildren().add(spacer);

        // Connection status pill
        header.getChildren().add(statusBadge);

        return header;
    }

    public void navigateTo(ViewType viewType) {
        if (viewType == null) return;
        this.currentView = viewType;

        // Update button styles
        for (Map.Entry<ViewType, Button> entry : navButtons.entrySet()) {
            if (entry.getKey() == viewType) {
                entry.getValue().getStyleClass().remove("nav-btn-active");
                entry.getValue().getStyleClass().add("nav-btn-active");
            } else {
                entry.getValue().getStyleClass().remove("nav-btn-active");
            }
        }

        // Get or build view
        Node view = viewCache.computeIfAbsent(viewType, this::createView);
        setCenter(view);
    }

    private Node createView(ViewType viewType) {
        return switch (viewType) {
            case HOME -> new HomeView(apiClient, statusBadge, this::navigateTo);
            case TEXT_ANALYSIS -> new TextAnalysisView(apiClient);
            case DOCUMENT_ANALYSIS -> new DocumentAnalysisView(apiClient);
            case CORPUS_SEARCH -> new CorpusSearchView(apiClient);
            case SETTINGS -> new SettingsView(apiClient, statusBadge);
        };
    }

    public ConnectionStatusBadge getStatusBadge() {
        return statusBadge;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }
}

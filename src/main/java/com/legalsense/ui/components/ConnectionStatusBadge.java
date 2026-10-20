package com.legalsense.ui.components;

import com.legalsense.client.ApiClient;
import com.legalsense.model.HealthResponse;
import javafx.application.Platform;
import javafx.scene.control.Label;
import javafx.scene.control.Tooltip;

/**
 * Visual badge indicating current Flask backend connectivity.
 */
public class ConnectionStatusBadge extends Label {

    public ConnectionStatusBadge() {
        setChecking();
    }

    public void setChecking() {
        setText("● Checking...");
        getStyleClass().removeAll("status-pill-online", "status-pill-offline", "status-pill-checking");
        getStyleClass().add("status-pill-checking");
        setTooltip(new Tooltip("Verifying connection to LegalSense backend..."));
    }

    public void setOnline(HealthResponse health) {
        String details = health.isWsdReady() ? "WSD Ready" : "WordNet Loading";
        if (health.isLlmEnabled()) {
            details += " | Groq LLM Active";
        }
        setText("● Backend Online (" + details + ")");
        getStyleClass().removeAll("status-pill-online", "status-pill-offline", "status-pill-checking");
        getStyleClass().add("status-pill-online");
        setTooltip(new Tooltip("Service: " + health.getService() + "\nStatus: " + health.getStatus()));
    }

    public void setOffline(String error) {
        setText("● Backend Disconnected");
        getStyleClass().removeAll("status-pill-online", "status-pill-offline", "status-pill-checking");
        getStyleClass().add("status-pill-offline");
        setTooltip(new Tooltip(error != null ? error : "Cannot reach backend. Check settings or start Flask service."));
    }

    public void refreshStatus(ApiClient client) {
        setChecking();
        client.checkHealth().whenComplete((health, ex) -> {
            Platform.runLater(() -> {
                if (ex != null || health == null || !health.isHealthy()) {
                    String msg = ex != null ? ex.getMessage() : "Unhealthy response";
                    setOffline(msg);
                } else {
                    setOnline(health);
                }
            });
        });
    }
}

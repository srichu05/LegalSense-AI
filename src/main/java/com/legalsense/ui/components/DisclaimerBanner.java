package com.legalsense.ui.components;

import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.layout.HBox;

/**
 * Informational-use legal research disclaimer banner displayed consistently at the bottom of the app.
 */
public class DisclaimerBanner extends HBox {

    public DisclaimerBanner() {
        setAlignment(Pos.CENTER);
        getStyleClass().add("banner-disclaimer");

        Label label = new Label("⚖ LegalSense is an academic legal NLP research tool. It does not provide legal advice or authoritative interpretations.");
        label.setStyle("-fx-text-fill: #64748B; -fx-font-size: 11px;");
        getChildren().add(label);
    }
}

package com.legalsense;

import com.legalsense.client.ApiClient;
import com.legalsense.ui.MainLayout;
import javafx.application.Application;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.net.URL;

/**
 * Main JavaFX Application class for LegalSense Desktop Client.
 */
public class LegalSenseApp extends Application {

    @Override
    public void start(Stage primaryStage) {
        // Allow overriding base URL from environment variable
        String envUrl = System.getenv("LEGALSENSE_API_URL");
        String baseUrl = (envUrl != null && !envUrl.isBlank()) ? envUrl.trim() : ApiClient.DEFAULT_BASE_URL;

        ApiClient apiClient = new ApiClient(baseUrl);
        MainLayout root = new MainLayout(apiClient);

        Scene scene = new Scene(root, 1120, 760);

        // Load stylesheet
        URL cssUrl = getClass().getResource("/styles/app.css");
        if (cssUrl != null) {
            scene.getStylesheets().add(cssUrl.toExternalForm());
        }

        primaryStage.setTitle("LegalSense — Context-Aware Legal NLP & Word Sense Disambiguation");
        primaryStage.setMinWidth(900);
        primaryStage.setMinHeight(640);
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}

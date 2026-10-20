package com.legalsense.ui.views;

import com.legalsense.client.ApiClient;
import com.legalsense.client.ApiException;
import com.legalsense.model.DocumentAnalyzeResponse;
import com.legalsense.model.WsdResultDto;
import com.legalsense.ui.components.SenseDetailCard;
import javafx.application.Platform;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

/**
 * Document Analysis workspace allowing users to select .txt and .pdf files,
 * submit them for ingestion and WSD scanning, and inspect passage-level occurrences.
 */
public class DocumentAnalysisView extends ScrollPane {

    private final ApiClient apiClient;

    private File selectedFile;
    private final Label selectedFileLabel;
    private final Button selectFileBtn;
    private final Button analyzeDocBtn;
    private final CheckBox useLlmCheckBox;
    private final ProgressIndicator progressIndicator;

    private final VBox metadataContainer;
    private final VBox warningsContainer;
    private final TableView<WsdResultDto> occurrencesTable;
    private final VBox occurrenceDetailContainer;
    private final ObservableList<WsdResultDto> occurrencesData = FXCollections.observableArrayList();

    public DocumentAnalysisView(ApiClient apiClient) {
        this.apiClient = apiClient;
        setFitToWidth(true);
        setStyle("-fx-background-color: transparent; -fx-background: transparent;");

        VBox content = new VBox(16);
        content.setPadding(new Insets(20));
        content.setMaxWidth(960);

        // Section Title
        VBox titleBox = new VBox(4);
        Label title = new Label("Document Ingestion & Legal Terminology Scanning");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold; -fx-text-fill: #0F172A;");
        Label subtitle = new Label("Upload plain text (.txt) or PDF (.pdf) legal instruments for passage segmentation and glossary occurrence analysis.");
        subtitle.setStyle("-fx-font-size: 12px; -fx-text-fill: #64748B;");
        titleBox.getChildren().addAll(title, subtitle);
        content.getChildren().add(titleBox);

        // File Selection Card
        VBox uploadCard = new VBox(12);
        uploadCard.getStyleClass().add("card");

        Label uploadHeader = new Label("Select Legal Document");
        uploadHeader.setStyle("-fx-font-weight: bold; -fx-text-fill: #334155;");

        HBox fileSelectRow = new HBox(12);
        fileSelectRow.setAlignment(Pos.CENTER_LEFT);

        selectFileBtn = new Button("Choose File (.txt, .pdf)...");
        selectFileBtn.getStyleClass().add("btn-secondary");
        selectFileBtn.setOnAction(e -> chooseFile());

        selectedFileLabel = new Label("No document selected.");
        selectedFileLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #64748B;");

        fileSelectRow.getChildren().addAll(selectFileBtn, selectedFileLabel);

        // Sample documents shortcut row
        HBox sampleDocsRow = new HBox(10);
        sampleDocsRow.setAlignment(Pos.CENTER_LEFT);
        Label samplePrompt = new Label("Bundled samples:");
        samplePrompt.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B;");

        Button loadSampleContract = new Button("sample_contract.txt");
        loadSampleContract.getStyleClass().add("btn-secondary");
        loadSampleContract.setStyle("-fx-font-size: 11px; -fx-padding: 3px 8px;");
        loadSampleContract.setOnAction(e -> loadSampleFile("data/sample_documents/sample_contract.txt"));

        Button loadSampleRuling = new Button("sample_court_ruling.txt");
        loadSampleRuling.getStyleClass().add("btn-secondary");
        loadSampleRuling.setStyle("-fx-font-size: 11px; -fx-padding: 3px 8px;");
        loadSampleRuling.setOnAction(e -> loadSampleFile("data/sample_documents/sample_court_ruling.txt"));

        sampleDocsRow.getChildren().addAll(samplePrompt, loadSampleContract, loadSampleRuling);

        // Upload actions row
        HBox actionRow = new HBox(16);
        actionRow.setAlignment(Pos.CENTER_LEFT);

        useLlmCheckBox = new CheckBox("Request Groq LLM assistance (if enabled on backend)");
        useLlmCheckBox.setStyle("-fx-font-size: 12px; -fx-text-fill: #334155;");

        analyzeDocBtn = new Button("Analyze Document");
        analyzeDocBtn.getStyleClass().add("btn-primary");
        analyzeDocBtn.setDisable(true);
        analyzeDocBtn.setOnAction(e -> runDocumentAnalysis());

        progressIndicator = new ProgressIndicator();
        progressIndicator.setPrefSize(22, 22);
        progressIndicator.setVisible(false);

        actionRow.getChildren().addAll(analyzeDocBtn, useLlmCheckBox, progressIndicator);

        uploadCard.getChildren().addAll(uploadHeader, fileSelectRow, sampleDocsRow, actionRow);
        content.getChildren().add(uploadCard);

        // Warnings container
        warningsContainer = new VBox(8);
        content.getChildren().add(warningsContainer);

        // Metadata container
        metadataContainer = new VBox(8);
        content.getChildren().add(metadataContainer);

        // Occurrences Table and Detail Section
        VBox tableSection = new VBox(10);
        tableSection.getStyleClass().add("card");

        Label occurrencesTitle = new Label("Analyzed Term Occurrences");
        occurrencesTitle.getStyleClass().add("card-title");

        occurrencesTable = createOccurrencesTable();
        occurrencesTable.setItems(occurrencesData);
        occurrencesTable.setPrefHeight(180);

        occurrencesTable.getSelectionModel().selectedItemProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal != null) {
                renderOccurrenceDetail(newVal);
            }
        });

        tableSection.getChildren().addAll(occurrencesTitle, occurrencesTable);
        content.getChildren().add(tableSection);

        // Occurrence Detail Container
        occurrenceDetailContainer = new VBox(10);
        content.getChildren().add(occurrenceDetailContainer);

        setContent(content);
    }

    private void chooseFile() {
        FileChooser chooser = new FileChooser();
        chooser.setTitle("Select Legal Document");
        chooser.getExtensionFilters().addAll(
                new FileChooser.ExtensionFilter("Legal Documents (*.txt, *.pdf)", "*.txt", "*.pdf"),
                new FileChooser.ExtensionFilter("Text Files (*.txt)", "*.txt"),
                new FileChooser.ExtensionFilter("PDF Documents (*.pdf)", "*.pdf")
        );

        File file = chooser.showOpenDialog(getScene() != null ? getScene().getWindow() : null);
        if (file != null) {
            setFile(file);
        }
    }

    private void loadSampleFile(String relativePath) {
        Path p = Paths.get(relativePath);
        if (!p.toFile().exists()) {
            // Check from project root
            p = Paths.get("..", relativePath);
        }
        if (p.toFile().exists()) {
            setFile(p.toFile());
        } else {
            showError("Sample File", "Sample document not found at: " + relativePath);
        }
    }

    private void setFile(File file) {
        this.selectedFile = file;
        long bytes = file.length();
        String sizeFormatted = bytes < 1024 ? bytes + " B" : (bytes / 1024) + " KB";
        selectedFileLabel.setText(file.getName() + " (" + sizeFormatted + ") - " + file.getAbsolutePath());
        selectedFileLabel.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #1E3A8A;");
        analyzeDocBtn.setDisable(false);
    }

    private TableView<WsdResultDto> createOccurrencesTable() {
        TableView<WsdResultDto> table = new TableView<>();

        TableColumn<WsdResultDto, String> colTerm = new TableColumn<>("Term");
        colTerm.setPrefWidth(120);
        colTerm.setCellValueFactory(data -> new SimpleStringProperty(data.getValue().getTerm()));

        TableColumn<WsdResultDto, String> colPage = new TableColumn<>("Page");
        colPage.setPrefWidth(60);
        colPage.setCellValueFactory(data -> new SimpleStringProperty(
                data.getValue().getPage() != null ? String.valueOf(data.getValue().getPage()) : "N/A"));

        TableColumn<WsdResultDto, String> colSense = new TableColumn<>("Selected Sense");
        colSense.setPrefWidth(160);
        colSense.setCellValueFactory(data -> {
            WsdResultDto res = data.getValue();
            if (res.getSelectedSense() != null) {
                return new SimpleStringProperty(res.getSelectedSense().getSynsetId());
            }
            return new SimpleStringProperty("None");
        });

        TableColumn<WsdResultDto, String> colConf = new TableColumn<>("Confidence");
        colConf.setPrefWidth(110);
        colConf.setCellValueFactory(data -> new SimpleStringProperty(
                data.getValue().isUncertain() ? "⚠ Low / Tied" : "Normal"));

        TableColumn<WsdResultDto, String> colSentence = new TableColumn<>("Passage Context");
        colSentence.setPrefWidth(420);
        colSentence.setCellValueFactory(data -> new SimpleStringProperty(
                data.getValue().getSentence() != null ? data.getValue().getSentence() : ""));

        table.getColumns().addAll(colTerm, colPage, colSense, colConf, colSentence);
        table.setPlaceholder(new Label("No document analyzed yet. Select a file and click 'Analyze Document'."));
        return table;
    }

    private void runDocumentAnalysis() {
        if (selectedFile == null || !selectedFile.exists()) {
            showError("File Error", "Please choose a valid file to analyze.");
            return;
        }

        setLoading(true);
        warningsContainer.getChildren().clear();
        metadataContainer.getChildren().clear();
        occurrencesData.clear();
        occurrenceDetailContainer.getChildren().clear();

        boolean useLlm = useLlmCheckBox.isSelected();

        apiClient.analyzeDocument(selectedFile.toPath(), useLlm)
                .whenComplete((response, ex) -> {
                    Platform.runLater(() -> {
                        setLoading(false);
                        if (ex != null) {
                            handleError(ex);
                        } else {
                            renderDocumentResults(response);
                        }
                    });
                });
    }

    private void renderDocumentResults(DocumentAnalyzeResponse response) {
        if (response == null) return;

        // Warnings banner (e.g. scanned PDF warning)
        if (response.getWarnings() != null && !response.getWarnings().isEmpty()) {
            for (String w : response.getWarnings()) {
                Label warn = new Label("Notice: " + w);
                warn.getStyleClass().add("banner-warning");
                warn.setMaxWidth(Double.MAX_VALUE);
                warningsContainer.getChildren().add(warn);
            }
        }

        // Metadata grid
        GridPane metaGrid = new GridPane();
        metaGrid.setHgap(20);
        metaGrid.setVgap(8);
        metaGrid.getStyleClass().add("card");

        metaGrid.add(createMetaLabel("Document ID:", response.getDocumentId()), 0, 0);
        metaGrid.add(createMetaLabel("Filename:", response.getFilename()), 1, 0);
        metaGrid.add(createMetaLabel("Format:", response.getFileType() != null ? response.getFileType().toUpperCase() : "TXT"), 2, 0);

        metaGrid.add(createMetaLabel("Characters:", String.format("%,d", response.getCharacterCount())), 0, 1);
        metaGrid.add(createMetaLabel("Pages:", String.valueOf(response.getPageCount())), 1, 1);
        metaGrid.add(createMetaLabel("Passages:", String.valueOf(response.getPassageCount())), 2, 1);

        metadataContainer.getChildren().add(metaGrid);

        // Populate table
        List<WsdResultDto> occurrences = response.getOccurrencesAnalyzed();
        if (occurrences != null && !occurrences.isEmpty()) {
            occurrencesData.addAll(occurrences);
            occurrencesTable.getSelectionModel().select(0);
        } else {
            Label noOcc = new Label("No legal glossary terms or ambiguous occurrences were detected in this document.");
            noOcc.setStyle("-fx-font-style: italic; -fx-text-fill: #64748B; -fx-padding: 10px;");
            occurrenceDetailContainer.getChildren().add(noOcc);
        }
    }

    private HBox createMetaLabel(String label, String value) {
        HBox box = new HBox(6);
        box.setAlignment(Pos.CENTER_LEFT);
        Label l = new Label(label);
        l.setStyle("-fx-font-weight: bold; -fx-text-fill: #64748B; -fx-font-size: 11px;");
        Label v = new Label(value != null ? value : "N/A");
        v.setStyle("-fx-font-weight: bold; -fx-text-fill: #0F172A; -fx-font-size: 12px;");
        box.getChildren().addAll(l, v);
        return box;
    }

    private void renderOccurrenceDetail(WsdResultDto occurrence) {
        occurrenceDetailContainer.getChildren().clear();

        Label detailHeader = new Label("Occurrence Detail: " + occurrence.getTerm());
        detailHeader.setStyle("-fx-font-size: 14px; -fx-font-weight: bold; -fx-text-fill: #1E293B;");

        SenseDetailCard card = new SenseDetailCard(occurrence);
        occurrenceDetailContainer.getChildren().addAll(detailHeader, card);
    }

    private void handleError(Throwable ex) {
        Throwable cause = ex.getCause() != null ? ex.getCause() : ex;
        String message = cause.getMessage();

        if (cause instanceof ApiException apiEx) {
            message = apiEx.getUserFacingMessage();
        }

        showError("Document Processing Error", message);
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
        warningsContainer.getChildren().add(errBox);
    }

    private void setLoading(boolean loading) {
        progressIndicator.setVisible(loading);
        analyzeDocBtn.setDisable(loading);
        selectFileBtn.setDisable(loading);
    }
}

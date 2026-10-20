package com.legalsense.client;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.legalsense.model.*;
import com.legalsense.util.JsonUtils;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Dedicated asynchronous HTTP client for the LegalSense REST API using java.net.http.HttpClient.
 * Communicates with the endpoints specified in docs/API_SPEC.md:
 * - GET /health
 * - POST /api/v1/analyze
 * - POST /api/v1/documents/analyze
 * - POST /api/v1/search
 */
public class ApiClient {

    public static final String DEFAULT_BASE_URL = "http://127.0.0.1:5000";
    private static final Duration CONNECT_TIMEOUT = Duration.ofSeconds(5);
    private static final Duration REQUEST_TIMEOUT = Duration.ofSeconds(30);

    private String baseUrl;
    private final HttpClient httpClient;

    public ApiClient() {
        this(DEFAULT_BASE_URL);
    }

    public ApiClient(String baseUrl) {
        this(baseUrl, HttpClient.newBuilder()
                .connectTimeout(CONNECT_TIMEOUT)
                .build());
    }

    public ApiClient(String baseUrl, HttpClient httpClient) {
        setBaseUrl(baseUrl);
        this.httpClient = httpClient;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public synchronized void setBaseUrl(String url) {
        if (url == null || url.isBlank()) {
            this.baseUrl = DEFAULT_BASE_URL;
        } else {
            String trimmed = url.trim();
            if (trimmed.endsWith("/")) {
                trimmed = trimmed.substring(0, trimmed.length() - 1);
            }
            this.baseUrl = trimmed;
        }
    }

    /**
     * GET /health - Lightweight health check.
     */
    public CompletableFuture<HealthResponse> checkHealth() {
        URI uri = URI.create(baseUrl + "/health");
        HttpRequest request = HttpRequest.newBuilder()
                .uri(uri)
                .timeout(REQUEST_TIMEOUT)
                .GET()
                .header("Accept", "application/json")
                .build();

        return sendAsync(request, HealthResponse.class);
    }

    /**
     * POST /api/v1/analyze - Analyze legal text and optionally disambiguate a target term.
     */
    public CompletableFuture<AnalyzeResponse> analyzeText(String text, String targetWord, boolean useLlm) {
        if (text == null || text.isBlank()) {
            CompletableFuture<AnalyzeResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException(400, "MISSING_TEXT", "Field 'text' is required and must not be empty."));
            return failed;
        }

        AnalyzeRequest req = new AnalyzeRequest(text.trim(), (targetWord != null && !targetWord.isBlank()) ? targetWord.trim() : null, useLlm);
        String jsonBody;
        try {
            jsonBody = JsonUtils.toJson(req);
        } catch (JsonProcessingException e) {
            CompletableFuture<AnalyzeResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException("Failed to serialize text analysis request", e));
            return failed;
        }

        URI uri = URI.create(baseUrl + "/api/v1/analyze");
        HttpRequest request = HttpRequest.newBuilder()
                .uri(uri)
                .timeout(REQUEST_TIMEOUT)
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody, StandardCharsets.UTF_8))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .build();

        return sendAsync(request, AnalyzeResponse.class);
    }

    /**
     * POST /api/v1/documents/analyze - Upload a .txt or .pdf file via multipart form data.
     */
    public CompletableFuture<DocumentAnalyzeResponse> analyzeDocument(Path filePath, boolean useLlm) {
        if (filePath == null || !Files.exists(filePath) || !Files.isRegularFile(filePath)) {
            CompletableFuture<DocumentAnalyzeResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException(400, "MISSING_FILE", "A valid document file must be selected."));
            return failed;
        }

        String filename = filePath.getFileName().toString();
        String lower = filename.toLowerCase();
        if (!lower.endsWith(".txt") && !lower.endsWith(".pdf")) {
            CompletableFuture<DocumentAnalyzeResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException(415, "UNSUPPORTED_FORMAT", "Only .txt and .pdf files are supported."));
            return failed;
        }

        byte[] fileBytes;
        try {
            fileBytes = Files.readAllBytes(filePath);
        } catch (IOException e) {
            CompletableFuture<DocumentAnalyzeResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException("Failed to read file: " + e.getMessage(), e));
            return failed;
        }

        if (fileBytes.length == 0) {
            CompletableFuture<DocumentAnalyzeResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException(400, "EMPTY_FILE", "Selected file is empty (0 bytes)."));
            return failed;
        }

        String boundary = "----LegalSenseBoundary" + UUID.randomUUID().toString().replace("-", "");
        byte[] multipartPayload = buildMultipartPayload(boundary, filename, fileBytes, useLlm);

        URI uri = URI.create(baseUrl + "/api/v1/documents/analyze");
        HttpRequest request = HttpRequest.newBuilder()
                .uri(uri)
                .timeout(REQUEST_TIMEOUT)
                .POST(HttpRequest.BodyPublishers.ofByteArray(multipartPayload))
                .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                .header("Accept", "application/json")
                .build();

        return sendAsync(request, DocumentAnalyzeResponse.class);
    }

    /**
     * POST /api/v1/search - Search legal passages across indexed corpus.
     */
    public CompletableFuture<SearchResponse> searchCorpus(String query, int topK) {
        if (query == null || query.isBlank()) {
            CompletableFuture<SearchResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException(400, "MISSING_QUERY", "Search query cannot be empty."));
            return failed;
        }

        SearchRequest req = new SearchRequest(query.trim(), topK, false);
        String jsonBody;
        try {
            jsonBody = JsonUtils.toJson(req);
        } catch (JsonProcessingException e) {
            CompletableFuture<SearchResponse> failed = new CompletableFuture<>();
            failed.completeExceptionally(new ApiException("Failed to serialize corpus search request", e));
            return failed;
        }

        URI uri = URI.create(baseUrl + "/api/v1/search");
        HttpRequest request = HttpRequest.newBuilder()
                .uri(uri)
                .timeout(REQUEST_TIMEOUT)
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody, StandardCharsets.UTF_8))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .build();

        return sendAsync(request, SearchResponse.class);
    }

    /**
     * Helper to send an HTTP request asynchronously and deserialize response.
     */
    private <T> CompletableFuture<T> sendAsync(HttpRequest request, Class<T> responseClass) {
        CompletableFuture<T> resultFuture = new CompletableFuture<>();

        httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .whenComplete((response, throwable) -> {
                    if (throwable != null) {
                        Throwable cause = throwable.getCause() != null ? throwable.getCause() : throwable;
                        resultFuture.completeExceptionally(new ApiException(0, "CONNECTION_FAILURE",
                                "Failed to connect to backend: " + cause.getMessage(), null, cause));
                        return;
                    }

                    int statusCode = response.statusCode();
                    String body = response.body();

                    if (statusCode >= 200 && statusCode < 300) {
                        try {
                            T parsed = JsonUtils.fromJson(body, responseClass);
                            resultFuture.complete(parsed);
                        } catch (JsonProcessingException e) {
                            resultFuture.completeExceptionally(new ApiException(statusCode, "MALFORMED_RESPONSE",
                                    "Server returned an unparseable response: " + e.getMessage(), body, e));
                        }
                    } else {
                        // Attempt to extract structured error code and message
                        String code = "HTTP_" + statusCode;
                        String message = "HTTP error " + statusCode;
                        try {
                            ErrorResponse err = JsonUtils.fromJson(body, ErrorResponse.class);
                            if (err != null && err.getError() != null) {
                                if (err.getError().getCode() != null) code = err.getError().getCode();
                                if (err.getError().getMessage() != null) message = err.getError().getMessage();
                            }
                        } catch (Exception ignored) {
                            if (body != null && !body.isBlank() && body.length() < 200) {
                                message = body.trim();
                            }
                        }
                        resultFuture.completeExceptionally(new ApiException(statusCode, code, message, body));
                    }
                });

        return resultFuture;
    }

    /**
     * Builds RFC 7578 multipart/form-data payload with 'file' and 'use_llm' fields.
     */
    private byte[] buildMultipartPayload(String boundary, String filename, byte[] fileBytes, boolean useLlm) {
        String contentType = filename.toLowerCase().endsWith(".pdf") ? "application/pdf" : "text/plain";
        byte[] lineBreak = "\r\n".getBytes(StandardCharsets.UTF_8);
        byte[] boundaryBytes = ("--" + boundary + "\r\n").getBytes(StandardCharsets.UTF_8);

        StringBuilder sbFileHeader = new StringBuilder();
        sbFileHeader.append("--").append(boundary).append("\r\n");
        sbFileHeader.append("Content-Disposition: form-data; name=\"file\"; filename=\"").append(filename).append("\"\r\n");
        sbFileHeader.append("Content-Type: ").append(contentType).append("\r\n\r\n");
        byte[] fileHeader = sbFileHeader.toString().getBytes(StandardCharsets.UTF_8);

        StringBuilder sbLlm = new StringBuilder();
        sbLlm.append("\r\n--").append(boundary).append("\r\n");
        sbLlm.append("Content-Disposition: form-data; name=\"use_llm\"\r\n\r\n");
        sbLlm.append(useLlm ? "true" : "false").append("\r\n");
        sbLlm.append("--").append(boundary).append("--\r\n");
        byte[] llmAndClosing = sbLlm.toString().getBytes(StandardCharsets.UTF_8);

        byte[] payload = new byte[fileHeader.length + fileBytes.length + llmAndClosing.length];
        System.arraycopy(fileHeader, 0, payload, 0, fileHeader.length);
        System.arraycopy(fileBytes, 0, payload, fileHeader.length, fileBytes.length);
        System.arraycopy(llmAndClosing, 0, payload, fileHeader.length + fileBytes.length, llmAndClosing.length);

        return payload;
    }

}

package com.legalsense.client;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.legalsense.model.*;
import com.legalsense.util.JsonUtils;
import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.ExecutionException;

import static org.junit.jupiter.api.Assertions.*;

public class ApiClientTest {

    private static HttpServer mockServer;
    private static String mockServerUrl;

    @BeforeAll
    static void startMockServer() throws IOException {
        mockServer = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        // /health handler
        mockServer.createContext("/health", exchange -> {
            String resp = "{\"status\":\"ok\",\"service\":\"legalsense-api\",\"wsd_ready\":true,\"llm_enabled\":false}";
            byte[] bytes = resp.getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(bytes);
            }
        });

        // /api/v1/analyze handler
        mockServer.createContext("/api/v1/analyze", exchange -> {
            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(405, -1);
                return;
            }
            byte[] reqBytes = exchange.getRequestBody().readAllBytes();
            String reqBody = new String(reqBytes, StandardCharsets.UTF_8);

            if (reqBody.contains("trigger_error")) {
                String err = "{\"error\":{\"code\":\"INVALID_REQUEST\",\"message\":\"Triggered error for testing.\"}}";
                byte[] bytes = err.getBytes(StandardCharsets.UTF_8);
                exchange.getResponseHeaders().set("Content-Type", "application/json");
                exchange.sendResponseHeaders(400, bytes.length);
                try (OutputStream os = exchange.getResponseBody()) {
                    os.write(bytes);
                }
                return;
            }

            String resp = "{\n" +
                    "  \"request_id\": \"test-req-123\",\n" +
                    "  \"results\": [\n" +
                    "    {\n" +
                    "      \"term\": \"consideration\",\n" +
                    "      \"sentence\": \"The contract included consideration.\",\n" +
                    "      \"pos\": \"NOUN\",\n" +
                    "      \"lemma\": \"consideration\",\n" +
                    "      \"candidate_senses\": [\n" +
                    "        {\n" +
                    "          \"source\": \"wordnet\",\n" +
                    "          \"synset_id\": \"consideration.n.01\",\n" +
                    "          \"definition\": \"the process of giving careful thought to something\",\n" +
                    "          \"pos\": \"NOUN\",\n" +
                    "          \"score\": 2.5,\n" +
                    "          \"rank\": 1,\n" +
                    "          \"relations\": {\n" +
                    "            \"synonyms\": [\"thoughtfulness\"],\n" +
                    "            \"hypernyms\": [\"thinking.n.01\"],\n" +
                    "            \"hyponyms\": []\n" +
                    "          }\n" +
                    "        }\n" +
                    "      ],\n" +
                    "      \"selected_sense\": {\n" +
                    "        \"source\": \"wordnet\",\n" +
                    "        \"synset_id\": \"consideration.n.01\",\n" +
                    "        \"definition\": \"the process of giving careful thought to something\",\n" +
                    "        \"pos\": \"NOUN\",\n" +
                    "        \"score\": 2.5,\n" +
                    "        \"rank\": 1,\n" +
                    "        \"relations\": {\n" +
                    "          \"synonyms\": [\"thoughtfulness\"],\n" +
                    "          \"hypernyms\": [\"thinking.n.01\"],\n" +
                    "          \"hyponyms\": []\n" +
                    "        }\n" +
                    "      },\n" +
                    "      \"selection_method\": \"extended_lesk\",\n" +
                    "      \"evidence\": [\n" +
                    "        {\n" +
                    "          \"candidate_synset_id\": \"consideration.n.01\",\n" +
                    "          \"overlap_tokens\": [\"contract\"],\n" +
                    "          \"overlap_source\": \"definition\",\n" +
                    "          \"contribution\": 1.0\n" +
                    "        }\n" +
                    "      ],\n" +
                    "      \"uncertain\": false,\n" +
                    "      \"source_provenance\": [\"wordnet\"],\n" +
                    "      \"legal_glossary_entry\": {\n" +
                    "        \"term\": \"consideration\",\n" +
                    "        \"definition\": \"Something of value exchanged between parties.\",\n" +
                    "        \"jurisdiction\": \"Common law\",\n" +
                    "        \"source\": \"Black's Law Dictionary\",\n" +
                    "        \"usage_example\": \"The buyer gave consideration.\",\n" +
                    "        \"limitations\": \"Educational summary.\"\n" +
                    "      },\n" +
                    "      \"llm_assistance_status\": \"disabled\"\n" +
                    "    }\n" +
                    "  ],\n" +
                    "  \"warnings\": []\n" +
                    "}";

            byte[] bytes = resp.getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(bytes);
            }
        });

        // /api/v1/documents/analyze handler
        mockServer.createContext("/api/v1/documents/analyze", exchange -> {
            String resp = "{\n" +
                    "  \"request_id\": \"doc-req-456\",\n" +
                    "  \"document_id\": \"doc_abc123\",\n" +
                    "  \"filename\": \"test_contract.txt\",\n" +
                    "  \"file_type\": \"txt\",\n" +
                    "  \"character_count\": 500,\n" +
                    "  \"page_count\": 1,\n" +
                    "  \"passage_count\": 2,\n" +
                    "  \"occurrences_analyzed\": [\n" +
                    "    {\n" +
                    "      \"term\": \"consideration\",\n" +
                    "      \"page\": 1,\n" +
                    "      \"passage_id\": \"doc_abc123_p001\",\n" +
                    "      \"sentence\": \"The parties provide consideration.\",\n" +
                    "      \"pos\": \"NOUN\",\n" +
                    "      \"lemma\": \"consideration\",\n" +
                    "      \"candidate_senses\": [],\n" +
                    "      \"uncertain\": true,\n" +
                    "      \"source_provenance\": [\"wordnet\"]\n" +
                    "    }\n" +
                    "  ],\n" +
                    "  \"warnings\": [\"Document parsed successfully.\"]\n" +
                    "}";

            byte[] bytes = resp.getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(bytes);
            }
        });

        // /api/v1/search handler
        mockServer.createContext("/api/v1/search", exchange -> {
            String resp = "{\n" +
                    "  \"query\": \"consideration clause\",\n" +
                    "  \"results\": [\n" +
                    "    {\n" +
                    "      \"document_id\": \"doc_1\",\n" +
                    "      \"document_name\": \"sample_contract.txt\",\n" +
                    "      \"page\": 1,\n" +
                    "      \"passage\": \"This contract involves mutual consideration between the parties.\",\n" +
                    "      \"score\": 0.8521,\n" +
                    "      \"score_method\": \"tfidf_lexical_wsd\",\n" +
                    "      \"matched_terms\": [\"consideration\", \"contract\"]\n" +
                    "    }\n" +
                    "  ],\n" +
                    "  \"warnings\": []\n" +
                    "}";

            byte[] bytes = resp.getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(bytes);
            }
        });

        mockServer.start();
        int port = mockServer.getAddress().getPort();
        mockServerUrl = "http://127.0.0.1:" + port;
    }

    @AfterAll
    static void stopMockServer() {
        if (mockServer != null) {
            mockServer.stop(0);
        }
    }

    @Test
    void testBaseUrlSanitization() {
        ApiClient client = new ApiClient("http://localhost:5000/");
        assertEquals("http://localhost:5000", client.getBaseUrl());

        client.setBaseUrl("http://127.0.0.1:8080/  ");
        assertEquals("http://127.0.0.1:8080", client.getBaseUrl());

        client.setBaseUrl("");
        assertEquals(ApiClient.DEFAULT_BASE_URL, client.getBaseUrl());
    }

    @Test
    void testCheckHealthSuccess() throws Exception {
        ApiClient client = new ApiClient(mockServerUrl);
        HealthResponse health = client.checkHealth().get();

        assertNotNull(health);
        assertEquals("ok", health.getStatus());
        assertEquals("legalsense-api", health.getService());
        assertTrue(health.isWsdReady());
        assertFalse(health.isLlmEnabled());
        assertTrue(health.isHealthy());
    }

    @Test
    void testAnalyzeTextSuccess() throws Exception {
        ApiClient client = new ApiClient(mockServerUrl);
        AnalyzeResponse response = client.analyzeText("The contract included consideration.", "consideration", false).get();

        assertNotNull(response);
        assertEquals("test-req-123", response.getRequestId());
        assertEquals(1, response.getResults().size());

        WsdResultDto result = response.getResults().get(0);
        assertEquals("consideration", result.getTerm());
        assertEquals("extended_lesk", result.getSelectionMethod());
        assertNotNull(result.getSelectedSense());
        assertEquals("consideration.n.01", result.getSelectedSense().getSynsetId());
        assertEquals(2.5, result.getSelectedSense().getScore());

        // Check lexical relations
        RelationsDto rels = result.getSelectedSense().getRelations();
        assertNotNull(rels);
        assertTrue(rels.getSynonyms().contains("thoughtfulness"));

        // Check legal glossary entry
        GlossaryEntryDto gloss = result.getLegalGlossaryEntry();
        assertNotNull(gloss);
        assertEquals("consideration", gloss.getTerm());
        assertEquals("Common law", gloss.getJurisdiction());
    }

    @Test
    void testAnalyzeTextValidationErrors() {
        ApiClient client = new ApiClient(mockServerUrl);

        // Empty text
        ExecutionException ex1 = assertThrows(ExecutionException.class, () -> client.analyzeText("", null, false).get());
        assertTrue(ex1.getCause() instanceof ApiException);
        ApiException apiEx1 = (ApiException) ex1.getCause();
        assertEquals(400, apiEx1.getStatusCode());
        assertEquals("MISSING_TEXT", apiEx1.getErrorCode());

        // Blank text
        ExecutionException ex2 = assertThrows(ExecutionException.class, () -> client.analyzeText("   ", null, false).get());
        assertTrue(ex2.getCause() instanceof ApiException);
    }

    @Test
    void testAnalyzeTextServerErrorHandling() {
        ApiClient client = new ApiClient(mockServerUrl);
        ExecutionException ex = assertThrows(ExecutionException.class,
                () -> client.analyzeText("trigger_error", null, false).get());

        assertTrue(ex.getCause() instanceof ApiException);
        ApiException apiEx = (ApiException) ex.getCause();
        assertEquals(400, apiEx.getStatusCode());
        assertEquals("INVALID_REQUEST", apiEx.getErrorCode());
        assertTrue(apiEx.getMessage().contains("Triggered error for testing."));
    }

    @Test
    void testAnalyzeDocumentSuccess(@TempDir Path tempDir) throws Exception {
        Path txtFile = tempDir.resolve("test_contract.txt");
        Files.writeString(txtFile, "The parties provide consideration.");

        ApiClient client = new ApiClient(mockServerUrl);
        DocumentAnalyzeResponse response = client.analyzeDocument(txtFile, false).get();

        assertNotNull(response);
        assertEquals("doc_abc123", response.getDocumentId());
        assertEquals("test_contract.txt", response.getFilename());
        assertEquals("txt", response.getFileType());
        assertEquals(1, response.getPageCount());
        assertEquals(2, response.getPassageCount());
        assertEquals(1, response.getOccurrencesAnalyzed().size());
        assertEquals(1, response.getOccurrencesAnalyzed().get(0).getPage());
        assertEquals("doc_abc123_p001", response.getOccurrencesAnalyzed().get(0).getPassageId());
    }

    @Test
    void testAnalyzeDocumentValidation(@TempDir Path tempDir) {
        ApiClient client = new ApiClient(mockServerUrl);

        // Null file
        ExecutionException ex1 = assertThrows(ExecutionException.class, () -> client.analyzeDocument(null, false).get());
        assertTrue(ex1.getCause() instanceof ApiException);

        // Unsupported extension
        Path badExt = tempDir.resolve("unsupported.docx");
        try {
            Files.writeString(badExt, "content");
        } catch (IOException ignored) {}
        ExecutionException ex2 = assertThrows(ExecutionException.class, () -> client.analyzeDocument(badExt, false).get());
        assertTrue(ex2.getCause() instanceof ApiException);
        assertEquals(415, ((ApiException) ex2.getCause()).getStatusCode());

        // Empty file
        Path emptyFile = tempDir.resolve("empty.txt");
        try {
            Files.createFile(emptyFile);
        } catch (IOException ignored) {}
        ExecutionException ex3 = assertThrows(ExecutionException.class, () -> client.analyzeDocument(emptyFile, false).get());
        assertTrue(ex3.getCause() instanceof ApiException);
        assertEquals(400, ((ApiException) ex3.getCause()).getStatusCode());
    }

    @Test
    void testSearchCorpusSuccess() throws Exception {
        ApiClient client = new ApiClient(mockServerUrl);
        SearchResponse response = client.searchCorpus("consideration clause", 5).get();

        assertNotNull(response);
        assertEquals("consideration clause", response.getQuery());
        assertEquals(1, response.getResults().size());

        SearchResultDto hit = response.getResults().get(0);
        assertEquals("doc_1", hit.getDocumentId());
        assertEquals("sample_contract.txt", hit.getDocumentName());
        assertEquals(0.8521, hit.getScore());
        assertTrue(hit.getMatchedTerms().contains("consideration"));
    }

    @Test
    void testSearchCorpusValidation() {
        ApiClient client = new ApiClient(mockServerUrl);
        ExecutionException ex = assertThrows(ExecutionException.class, () -> client.searchCorpus("", 5).get());
        assertTrue(ex.getCause() instanceof ApiException);
        assertEquals(400, ((ApiException) ex.getCause()).getStatusCode());
        assertEquals("MISSING_QUERY", ((ApiException) ex.getCause()).getErrorCode());
    }

    @Test
    void testConnectionFailureToUnreachablePort() {
        // Port 9999 is typically unused
        ApiClient client = new ApiClient("http://127.0.0.1:59999");
        ExecutionException ex = assertThrows(ExecutionException.class, () -> client.checkHealth().get());
        assertTrue(ex.getCause() instanceof ApiException);
        ApiException apiEx = (ApiException) ex.getCause();
        assertEquals(0, apiEx.getStatusCode());
        assertEquals("CONNECTION_FAILURE", apiEx.getErrorCode());
        assertTrue(apiEx.getUserFacingMessage().contains("Unable to connect to LegalSense backend"));
    }
}

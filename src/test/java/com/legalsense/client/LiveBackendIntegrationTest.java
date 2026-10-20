package com.legalsense.client;

import com.legalsense.model.AnalyzeResponse;
import com.legalsense.model.DocumentAnalyzeResponse;
import com.legalsense.model.HealthResponse;
import com.legalsense.model.SearchResponse;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

/**
 * End-to-end integration tests connecting to a live local Flask backend if active.
 * Automatically executed when Flask is running on http://127.0.0.1:5000,
 * and gracefully skipped if the local server is offline.
 */
public class LiveBackendIntegrationTest {

    private static final String LIVE_URL = "http://127.0.0.1:5000";
    private static boolean isLiveBackendAvailable = false;
    private static ApiClient liveClient;

    @BeforeAll
    static void checkLiveBackend() {
        liveClient = new ApiClient(LIVE_URL);
        try {
            HealthResponse health = liveClient.checkHealth().get(2, TimeUnit.SECONDS);
            isLiveBackendAvailable = (health != null && health.isHealthy());
        } catch (Exception e) {
            isLiveBackendAvailable = false;
        }
    }

    @Test
    void testLiveHealthCheck() throws Exception {
        Assumptions.assumeTrue(isLiveBackendAvailable, "Live Flask backend is not running on " + LIVE_URL);

        HealthResponse health = liveClient.checkHealth().get(5, TimeUnit.SECONDS);
        assertNotNull(health);
        assertEquals("ok", health.getStatus());
        assertEquals("legalsense-api", health.getService());
        assertTrue(health.isWsdReady());
    }

    @Test
    void testLiveTextAnalysis() throws Exception {
        Assumptions.assumeTrue(isLiveBackendAvailable, "Live Flask backend is not running on " + LIVE_URL);

        String text = "Both parties to the contract signed the legal agreement.";
        AnalyzeResponse response = liveClient.analyzeText(text, "party", false).get(10, TimeUnit.SECONDS);

        assertNotNull(response);
        assertNotNull(response.getRequestId());
        assertFalse(response.getResults().isEmpty());

        var result = response.getResults().get(0);
        assertEquals("party", result.getTerm());
        assertEquals("extended_lesk", result.getSelectionMethod());
        assertNotNull(result.getSelectedSense());
        assertNotNull(result.getSelectedSense().getSynsetId());
        assertNotNull(result.getLegalGlossaryEntry());
        assertEquals("party", result.getLegalGlossaryEntry().getTerm());
    }

    @Test
    void testLiveDocumentAnalysis() throws Exception {
        Assumptions.assumeTrue(isLiveBackendAvailable, "Live Flask backend is not running on " + LIVE_URL);

        Path sampleFile = Paths.get("data", "sample_documents", "sample_contract.txt");
        if (!Files.exists(sampleFile)) {
            sampleFile = Paths.get("..", "data", "sample_documents", "sample_contract.txt");
        }
        Assumptions.assumeTrue(Files.exists(sampleFile), "Sample contract document not found at: " + sampleFile);

        DocumentAnalyzeResponse response = liveClient.analyzeDocument(sampleFile, false).get(10, TimeUnit.SECONDS);

        assertNotNull(response);
        assertEquals("sample_contract.txt", response.getFilename());
        assertEquals("txt", response.getFileType());
        assertTrue(response.getCharacterCount() > 0);
        assertTrue(response.getPassageCount() > 0);
    }

    @Test
    void testLiveCorpusSearch() throws Exception {
        Assumptions.assumeTrue(isLiveBackendAvailable, "Live Flask backend is not running on " + LIVE_URL);

        SearchResponse response = liveClient.searchCorpus("consideration contract mutual promises", 3).get(10, TimeUnit.SECONDS);

        assertNotNull(response);
        assertFalse(response.getResults().isEmpty());
        var topHit = response.getResults().get(0);
        assertNotNull(topHit.getDocumentName());
        assertTrue(topHit.getScore() > 0.0);
        assertFalse(topHit.getMatchedTerms().isEmpty());
    }
}

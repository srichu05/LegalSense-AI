package com.legalsense.model;

import com.legalsense.util.JsonUtils;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class JsonModelTest {

    @Test
    void testHealthResponseDeserialization() throws Exception {
        String json = "{\"status\":\"ok\",\"service\":\"legalsense-api\",\"wsd_ready\":true,\"llm_enabled\":false,\"extra_unknown_field\":\"ignore_me\"}";
        HealthResponse resp = JsonUtils.fromJson(json, HealthResponse.class);

        assertNotNull(resp);
        assertEquals("ok", resp.getStatus());
        assertEquals("legalsense-api", resp.getService());
        assertTrue(resp.isWsdReady());
        assertFalse(resp.isLlmEnabled());
        assertTrue(resp.isHealthy());
    }

    @Test
    void testAnalyzeRequestSerialization() throws Exception {
        AnalyzeRequest req = new AnalyzeRequest("The contract requires consideration.", "consideration", false);
        String json = JsonUtils.toJson(req);

        assertTrue(json.contains("\"text\":\"The contract requires consideration.\""));
        assertTrue(json.contains("\"target_word\":\"consideration\""));
        assertTrue(json.contains("\"use_llm\":false"));
    }

    @Test
    void testAnalyzeResponseMissingOptionalFields() throws Exception {
        // Minimal JSON with missing optional fields
        String json = "{\"request_id\":\"req-123\",\"results\":[{\"term\":\"motion\",\"sentence\":\"He made a motion.\",\"pos\":\"NOUN\",\"lemma\":\"motion\"}]}";
        AnalyzeResponse resp = JsonUtils.fromJson(json, AnalyzeResponse.class);

        assertNotNull(resp);
        assertEquals("req-123", resp.getRequestId());
        assertEquals(1, resp.getResults().size());

        WsdResultDto result = resp.getResults().get(0);
        assertEquals("motion", result.getTerm());
        assertNull(result.getSelectedSense());
        assertNull(result.getLegalGlossaryEntry());
        assertNotNull(result.getCandidateSenses());
        assertTrue(result.getCandidateSenses().isEmpty());
        assertNotNull(result.getEvidence());
        assertTrue(result.getEvidence().isEmpty());
    }

    @Test
    void testCandidateSenseWithLexicalRelations() throws Exception {
        String json = "{\n" +
                "  \"source\": \"wordnet\",\n" +
                "  \"synset_id\": \"motion.n.06\",\n" +
                "  \"definition\": \"a formal proposal for action in a meeting\",\n" +
                "  \"pos\": \"NOUN\",\n" +
                "  \"score\": 3.1415,\n" +
                "  \"rank\": 1,\n" +
                "  \"relations\": {\n" +
                "    \"synonyms\": [\"proposal\"],\n" +
                "    \"hypernyms\": [\"request.n.01\"],\n" +
                "    \"hyponyms\": [\"filibuster.n.01\"]\n" +
                "  }\n" +
                "}";

        CandidateSenseDto sense = JsonUtils.fromJson(json, CandidateSenseDto.class);
        assertNotNull(sense);
        assertEquals("motion.n.06", sense.getSynsetId());
        assertEquals(1, sense.getRank());
        assertEquals(3.1415, sense.getScore(), 0.0001);

        assertNotNull(sense.getRelations());
        assertEquals(List.of("proposal"), sense.getRelations().getSynonyms());
        assertEquals(List.of("request.n.01"), sense.getRelations().getHypernyms());
        assertEquals(List.of("filibuster.n.01"), sense.getRelations().getHyponyms());
    }

    @Test
    void testLegalGlossaryEntryDeserialization() throws Exception {
        String json = "{\n" +
                "  \"term\": \"motion\",\n" +
                "  \"definition\": \"A formal application made to a judge or court requesting an order or ruling.\",\n" +
                "  \"jurisdiction\": \"General procedural law\",\n" +
                "  \"source\": \"Black's Law Dictionary\",\n" +
                "  \"usage_example\": \"The defense attorney filed a motion to suppress evidence.\",\n" +
                "  \"limitations\": \"Educational summary only.\"\n" +
                "}";

        GlossaryEntryDto entry = JsonUtils.fromJson(json, GlossaryEntryDto.class);
        assertNotNull(entry);
        assertEquals("motion", entry.getTerm());
        assertEquals("General procedural law", entry.getJurisdiction());
        assertEquals("Black's Law Dictionary", entry.getSource());
    }

    @Test
    void testDocumentAnalyzeResponseDeserialization() throws Exception {
        String json = "{\n" +
                "  \"request_id\": \"doc-uuid\",\n" +
                "  \"document_id\": \"doc_123\",\n" +
                "  \"filename\": \"brief.pdf\",\n" +
                "  \"file_type\": \"pdf\",\n" +
                "  \"character_count\": 12450,\n" +
                "  \"page_count\": 5,\n" +
                "  \"passage_count\": 18,\n" +
                "  \"occurrences_analyzed\": [],\n" +
                "  \"warnings\": [\"Document parsed in-memory.\"]\n" +
                "}";

        DocumentAnalyzeResponse docResp = JsonUtils.fromJson(json, DocumentAnalyzeResponse.class);
        assertNotNull(docResp);
        assertEquals("doc_123", docResp.getDocumentId());
        assertEquals(12450, docResp.getCharacterCount());
        assertEquals(5, docResp.getPageCount());
        assertEquals(18, docResp.getPassageCount());
        assertEquals(1, docResp.getWarnings().size());
    }

    @Test
    void testSearchRequestAndResponseSerialization() throws Exception {
        SearchRequest req = new SearchRequest("summary judgment", 10, false);
        String reqJson = JsonUtils.toJson(req);
        assertTrue(reqJson.contains("\"query\":\"summary judgment\""));
        assertTrue(reqJson.contains("\"top_k\":10"));

        String respJson = "{\n" +
                "  \"query\": \"summary judgment\",\n" +
                "  \"results\": [\n" +
                "    {\n" +
                "      \"document_id\": \"doc_ruling\",\n" +
                "      \"document_name\": \"sample_court_ruling.txt\",\n" +
                "      \"page\": null,\n" +
                "      \"passage\": \"The motion for summary judgment is hereby denied.\",\n" +
                "      \"score\": 0.725,\n" +
                "      \"score_method\": \"tfidf_lexical_wsd\",\n" +
                "      \"matched_terms\": [\"summary\", \"judgment\"]\n" +
                "    }\n" +
                "  ],\n" +
                "  \"warnings\": []\n" +
                "}";

        SearchResponse resp = JsonUtils.fromJson(respJson, SearchResponse.class);
        assertNotNull(resp);
        assertEquals("summary judgment", resp.getQuery());
        assertEquals(1, resp.getResults().size());
        SearchResultDto hit = resp.getResults().get(0);
        assertNull(hit.getPage());
        assertEquals(0.725, hit.getScore(), 0.001);
        assertEquals(List.of("summary", "judgment"), hit.getMatchedTerms());
    }

    @Test
    void testStandardErrorResponseDeserialization() throws Exception {
        String json = "{\"error\":{\"code\":\"FILE_TOO_LARGE\",\"message\":\"File size exceeds the 16 MB maximum upload limit.\"}}";
        ErrorResponse err = JsonUtils.fromJson(json, ErrorResponse.class);

        assertNotNull(err);
        assertNotNull(err.getError());
        assertEquals("FILE_TOO_LARGE", err.getError().getCode());
        assertEquals("File size exceeds the 16 MB maximum upload limit.", err.getError().getMessage());
    }
}

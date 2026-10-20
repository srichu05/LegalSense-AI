package com.legalsense.ui.components;

import com.legalsense.model.CandidateSenseDto;
import com.legalsense.model.EvidenceDto;
import com.legalsense.model.GlossaryEntryDto;
import com.legalsense.model.WsdResultDto;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.Separator;
import javafx.scene.layout.*;

import java.util.List;

/**
 * Detailed view component rendering a single WSD result, with explicit visual separation
 * between WordNet synset candidates, scoring evidence, and curated legal glossary information.
 */
public class SenseDetailCard extends VBox {

    public SenseDetailCard(WsdResultDto result) {
        setSpacing(14);
        setPadding(new Insets(16));
        getStyleClass().add("card");

        if (result == null) {
            Label empty = new Label("No sense information available.");
            getChildren().add(empty);
            return;
        }

        // Header Row: Term, Badges
        HBox headerRow = new HBox(10);
        headerRow.setAlignment(Pos.CENTER_LEFT);

        Label termLabel = new Label(result.getTerm() != null ? result.getTerm().toUpperCase() : "UNKNOWN TERM");
        termLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold; -fx-text-fill: #0F172A;");

        Label posBadge = new Label(result.getPos() != null ? result.getPos() : "POS");
        posBadge.getStyleClass().add("badge-wordnet");

        Label methodBadge = new Label("Method: " + (result.getSelectionMethod() != null ? result.getSelectionMethod() : "extended_lesk"));
        methodBadge.setStyle("-fx-background-color: #F1F5F9; -fx-text-fill: #475569; -fx-padding: 3px 8px; -fx-background-radius: 4px; -fx-font-size: 11px;");

        headerRow.getChildren().addAll(termLabel, posBadge, methodBadge);

        if (result.isUncertain()) {
            Label uncertBadge = new Label("⚠ Low Confidence / Tied Score");
            uncertBadge.getStyleClass().add("badge-uncertain");
            headerRow.getChildren().add(uncertBadge);
        }

        if (result.getPage() != null) {
            Label pageBadge = new Label("Page " + result.getPage());
            pageBadge.setStyle("-fx-background-color: #E0E7FF; -fx-text-fill: #3730A3; -fx-padding: 3px 8px; -fx-background-radius: 4px; -fx-font-size: 11px;");
            headerRow.getChildren().add(pageBadge);
        }

        getChildren().add(headerRow);

        // Sentence Context
        if (result.getSentence() != null && !result.getSentence().isBlank()) {
            VBox contextBox = new VBox(4);
            contextBox.setStyle("-fx-background-color: #F8FAFC; -fx-border-color: #E2E8F0; -fx-border-width: 1px; -fx-border-radius: 6px; -fx-background-radius: 6px; -fx-padding: 10px;");
            Label ctxTitle = new Label("SENTENCE CONTEXT:");
            ctxTitle.setStyle("-fx-font-size: 10px; -fx-font-weight: bold; -fx-text-fill: #64748B;");
            Label ctxText = new Label("\"" + result.getSentence() + "\"");
            ctxText.setWrapText(true);
            ctxText.setStyle("-fx-font-style: italic; -fx-text-fill: #1E293B;");
            contextBox.getChildren().addAll(ctxTitle, ctxText);
            getChildren().add(contextBox);
        }

        // Section A: Curated Legal Glossary (Visually Distinct amber styling)
        if (result.getLegalGlossaryEntry() != null) {
            getChildren().add(createLegalGlossarySection(result.getLegalGlossaryEntry()));
        }

        // Section B: WordNet Candidate Senses
        getChildren().add(createCandidateSensesSection(result));

        // Section C: Overlap Evidence
        if (result.getEvidence() != null && !result.getEvidence().isEmpty()) {
            getChildren().add(createEvidenceSection(result.getEvidence()));
        }

        // Section D: LLM Assistance Status / Rationale (if applicable)
        if (result.getLlmAssistanceStatus() != null && !"disabled".equalsIgnoreCase(result.getLlmAssistanceStatus())) {
            getChildren().add(createLlmSection(result));
        }
    }

    private VBox createLegalGlossarySection(GlossaryEntryDto entry) {
        VBox box = new VBox(8);
        box.getStyleClass().add("legal-glossary-card");

        HBox titleRow = new HBox(8);
        titleRow.setAlignment(Pos.CENTER_LEFT);
        Label badge = new Label("CURATED LEGAL GLOSSARY");
        badge.getStyleClass().add("badge-legal");

        Label jurisLabel = new Label(entry.getJurisdiction() != null ? "Jurisdiction: " + entry.getJurisdiction() : "");
        jurisLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #92400E;");
        titleRow.getChildren().addAll(badge, jurisLabel);

        Label defLabel = new Label(entry.getDefinition());
        defLabel.setWrapText(true);
        defLabel.setStyle("-fx-font-size: 13px; -fx-font-weight: 500; -fx-text-fill: #78350F;");

        box.getChildren().addAll(titleRow, defLabel);

        if (entry.getUsageExample() != null && !entry.getUsageExample().isBlank()) {
            Label exLabel = new Label("Example: " + entry.getUsageExample());
            exLabel.setWrapText(true);
            exLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #92400E; -fx-font-style: italic;");
            box.getChildren().add(exLabel);
        }

        if (entry.getSource() != null) {
            Label srcLabel = new Label("Source: " + entry.getSource());
            srcLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #B45309;");
            box.getChildren().add(srcLabel);
        }

        if (entry.getLimitations() != null) {
            Label limLabel = new Label("Limitations: " + entry.getLimitations());
            limLabel.setWrapText(true);
            limLabel.setStyle("-fx-font-size: 10px; -fx-text-fill: #92400E; -fx-font-style: italic;");
            box.getChildren().add(limLabel);
        }

        return box;
    }

    private VBox createCandidateSensesSection(WsdResultDto result) {
        VBox section = new VBox(8);

        Label header = new Label("WordNet Candidate Senses & Extended Lesk Ranking");
        header.setStyle("-fx-font-size: 13px; -fx-font-weight: bold; -fx-text-fill: #1E293B;");
        section.getChildren().add(header);

        List<CandidateSenseDto> candidates = result.getCandidateSenses();
        if (candidates == null || candidates.isEmpty()) {
            Label none = new Label("No WordNet candidate senses available for this term.");
            none.setStyle("-fx-text-fill: #64748B; -fx-font-style: italic;");
            section.getChildren().add(none);
            return section;
        }

        String selectedSynsetId = result.getSelectedSense() != null ? result.getSelectedSense().getSynsetId() : null;

        for (CandidateSenseDto sense : candidates) {
            VBox senseBox = new VBox(6);
            boolean isSelected = selectedSynsetId != null && selectedSynsetId.equals(sense.getSynsetId());

            if (isSelected) {
                senseBox.setStyle("-fx-background-color: #F0FDF4; -fx-border-color: #86EFAC; -fx-border-width: 1.5px; -fx-border-radius: 6px; -fx-background-radius: 6px; -fx-padding: 10px;");
            } else {
                senseBox.setStyle("-fx-background-color: #FFFFFF; -fx-border-color: #E2E8F0; -fx-border-width: 1px; -fx-border-radius: 6px; -fx-background-radius: 6px; -fx-padding: 10px;");
            }

            HBox senseHeader = new HBox(8);
            senseHeader.setAlignment(Pos.CENTER_LEFT);

            Label rankLabel = new Label("#" + sense.getRank());
            rankLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: #475569;");

            Label synsetLabel = new Label(sense.getSynsetId());
            synsetLabel.setStyle("-fx-font-family: monospace; -fx-font-weight: bold; -fx-text-fill: #1E3A8A;");

            Label scoreLabel = new Label(String.format("Score: %.4f", sense.getScore()));
            scoreLabel.setStyle("-fx-background-color: #EFF6FF; -fx-text-fill: #1E40AF; -fx-padding: 2px 6px; -fx-background-radius: 4px; -fx-font-size: 11px;");

            senseHeader.getChildren().addAll(rankLabel, synsetLabel, scoreLabel);

            if (isSelected) {
                Label selBadge = new Label("★ Selected Sense");
                selBadge.getStyleClass().add("badge-selected");
                senseHeader.getChildren().add(selBadge);
            }

            Label defLabel = new Label(sense.getDefinition());
            defLabel.setWrapText(true);
            defLabel.setStyle("-fx-text-fill: #334155; -fx-font-size: 12px;");

            senseBox.getChildren().addAll(senseHeader, defLabel);

            // Lexical relations
            if (sense.getRelations() != null) {
                HBox relsBox = new HBox(12);
                relsBox.setStyle("-fx-padding: 4px 0 0 0;");

                if (!sense.getRelations().getSynonyms().isEmpty()) {
                    Label syns = new Label("Synonyms: " + String.join(", ", sense.getRelations().getSynonyms()));
                    syns.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B;");
                    relsBox.getChildren().add(syns);
                }
                if (!sense.getRelations().getHypernyms().isEmpty()) {
                    Label hypers = new Label("Hypernyms: " + String.join(", ", sense.getRelations().getHypernyms()));
                    hypers.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B;");
                    relsBox.getChildren().add(hypers);
                }
                if (!sense.getRelations().getHyponyms().isEmpty()) {
                    Label hypos = new Label("Hyponyms: " + String.join(", ", sense.getRelations().getHyponyms()));
                    hypos.setStyle("-fx-font-size: 11px; -fx-text-fill: #64748B;");
                    relsBox.getChildren().add(hypos);
                }
                if (!relsBox.getChildren().isEmpty()) {
                    senseBox.getChildren().add(relsBox);
                }
            }

            section.getChildren().add(senseBox);
        }

        return section;
    }

    private VBox createEvidenceSection(List<EvidenceDto> evidenceList) {
        VBox section = new VBox(6);
        Label header = new Label("Scoring Evidence & Token Overlaps");
        header.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #475569;");
        section.getChildren().add(header);

        VBox evidenceCard = new VBox(4);
        evidenceCard.setStyle("-fx-background-color: #F8FAFC; -fx-border-color: #E2E8F0; -fx-border-width: 1px; -fx-border-radius: 6px; -fx-background-radius: 6px; -fx-padding: 8px 12px;");

        for (EvidenceDto ev : evidenceList) {
            String synset = ev.getCandidateSynsetId() != null ? ev.getCandidateSynsetId() : "target";
            String tokens = (ev.getOverlapTokens() != null && !ev.getOverlapTokens().isEmpty()) ?
                    String.join(", ", ev.getOverlapTokens()) : "none";
            String src = ev.getOverlapSource() != null ? ev.getOverlapSource() : "overlap";
            Label item = new Label(String.format("• [%s] Overlap on %s: {%s} (contribution: +%.2f)", synset, src, tokens, ev.getContribution()));
            item.setStyle("-fx-font-size: 11px; -fx-text-fill: #334155;");
            evidenceCard.getChildren().add(item);
        }

        section.getChildren().add(evidenceCard);
        return section;
    }

    private VBox createLlmSection(WsdResultDto result) {
        VBox box = new VBox(6);
        box.setStyle("-fx-background-color: #F5F3FF; -fx-border-color: #DDD6FE; -fx-border-width: 1px; -fx-border-radius: 6px; -fx-background-radius: 6px; -fx-padding: 10px;");

        HBox top = new HBox(8);
        top.setAlignment(Pos.CENTER_LEFT);
        Label badge = new Label("GROQ LLM ASSISTANCE");
        badge.setStyle("-fx-background-color: #EDE9FE; -fx-text-fill: #6D28D9; -fx-padding: 2px 6px; -fx-background-radius: 4px; -fx-font-size: 10px; -fx-font-weight: bold;");

        Label status = new Label("Status: " + result.getLlmAssistanceStatus());
        status.setStyle("-fx-font-size: 11px; -fx-text-fill: #5B21B6;");
        top.getChildren().addAll(badge, status);

        box.getChildren().add(top);

        if (result.getLlmSuggestedSense() != null) {
            Label sug = new Label("Suggested Synset: " + result.getLlmSuggestedSense());
            sug.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #4C1D95;");
            box.getChildren().add(sug);
        }

        if (result.getLlmRationale() != null) {
            Label rat = new Label("Model Rationale: " + result.getLlmRationale());
            rat.setWrapText(true);
            rat.setStyle("-fx-font-size: 11px; -fx-text-fill: #5B21B6; -fx-font-style: italic;");
            box.getChildren().add(rat);
        }

        return box;
    }
}

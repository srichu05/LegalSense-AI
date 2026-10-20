"""Download required NLP resources for LegalSense.

Run this script after installing dependencies:
    python scripts/setup_nlp_resources.py
"""

import sys


def main():
    print("=" * 60)
    print("LegalSense — NLP Resource Setup")
    print("=" * 60)

    # 1. NLTK resources
    print("\n[1/2] Downloading NLTK resources...")
    try:
        import nltk
        resources = ["wordnet", "punkt_tab", "averaged_perceptron_tagger_eng", "stopwords"]
        for resource in resources:
            print(f"  Downloading {resource}...", end=" ")
            nltk.download(resource, quiet=True)
            print("OK")
        # Verify WordNet is functional
        from nltk.corpus import wordnet as wn
        synsets = wn.synsets("test")
        print(f"  WordNet verification: {len(synsets)} synsets for 'test' — OK")
    except Exception as exc:
        print(f"\n  ERROR downloading NLTK resources: {exc}")
        print("  Try manually: python -c \"import nltk; nltk.download('wordnet')\"")
        sys.exit(1)

    # 2. spaCy model
    print("\n[2/2] Downloading spaCy English model...")
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("  en_core_web_sm already installed — OK")
        except OSError:
            print("  Model not found. Downloading en_core_web_sm...")
            from spacy.cli import download
            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
            print("  en_core_web_sm installed — OK")
        # Quick verification
        doc = nlp("The court issued a ruling.")
        print(f"  spaCy verification: {len(doc)} tokens — OK")
    except ImportError:
        print("  spaCy not installed. NLTK fallback will be used.")
        print("  To install: pip install spacy && python -m spacy download en_core_web_sm")
    except Exception as exc:
        print(f"  WARNING: spaCy setup failed ({exc}). NLTK fallback will be used.")

    print("\n" + "=" * 60)
    print("Setup complete. Run tests with: pytest tests/ -v")
    print("=" * 60)


if __name__ == "__main__":
    main()

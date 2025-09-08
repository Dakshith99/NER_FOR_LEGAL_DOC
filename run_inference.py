import spacy
import urllib.request
from legal_ner import extract_entities_from_judgment_text

# Load pretrained legal NER model
legal_nlp = spacy.load('en_legal_ner_trf')

# Load a sample judgment text
judgment_text = urllib.request.urlopen(
    'https://raw.githubusercontent.com/OpenNyAI/Opennyai/master/samples/sample_judgment1.txt'
).read().decode()

# Load model for preamble splitting
preamble_spiltting_nlp = spacy.load('en_core_web_sm')

# Run entity extraction
run_type = 'sent'  # 'sent' is more accurate, 'doc' is faster
do_postprocess = True

combined_doc = extract_entities_from_judgment_text(
    judgment_text,
    legal_nlp,
    preamble_spiltting_nlp,
    run_type,
    do_postprocess
)

# Print extracted entities in "Entity -> Label" format
print("\n📌 Extracted Entities:\n")
for ent in combined_doc.ents:
    print(f"{ent.text.strip()} -> {ent.label_}")

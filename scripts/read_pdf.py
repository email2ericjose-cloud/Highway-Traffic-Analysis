"""Read PDF and print full text for inspection."""
import pymupdf  # PyMuPDF

pdf_path = r"C:\Highway_Traffic_Analysis\input\DOC-20261009-WA0029.pdf"

doc = pymupdf.open(pdf_path)
print(f"Total pages: {len(doc)}")
print("=" * 80)

full_text = []
for i, page in enumerate(doc):
    text = page.get_text()
    full_text.append(f"\n{'='*60}\nPAGE {i+1}\n{'='*60}\n{text}")

all_text = "\n".join(full_text)
# print to file only, skip console print due to encoding
pass

# Save to file for inspection
with open(r"C:\Highway_Traffic_Analysis\scripts\pdf_extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"\nTotal chars: {len(all_text)}")

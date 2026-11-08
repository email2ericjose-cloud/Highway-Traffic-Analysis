from docx import Document
p='UAV_Traffic_Safety_Interim_Report_Combined.docx'
d=Document(p)
for i,x in enumerate(d.paragraphs):
 if 340 <= i <= 430 or 'CHAPTER-6' in x.text or 'CHAPTER-7' in x.text:
  print(i,repr(x.text[:300]),x.style.name)

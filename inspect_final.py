from docx import Document
from pathlib import Path
p=Path('UAV_Traffic_Safety_Project_Report_Revised.docx')
d=Document(p)
print(p.stat().st_size, 'bytes',len(d.paragraphs),'paras',len(d.tables),'tables',len(d.inline_shapes),'images')
for i,x in enumerate(d.paragraphs):
 if any(k in x.text.lower() for k in ['interim','updating contents','work done and expected','cvat is being','critical-limit','critical screening','expected results and deliverables','longitudinal and lateral']): print(i,repr(x.text[:200]),'break',x.paragraph_format.page_break_before,'style',x.style.name)
print('toc fields', [f.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instr') for f in d._element.xpath('.//w:fldSimple')])
print('new index lines:')
for x in d.paragraphs:
 if x.text.startswith(('5.2\t','6.3\t','6.4\t','6.5\t','6.6\t')): print(repr(x.text),x.style.name,x.paragraph_format.page_break_before)

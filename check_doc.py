from zipfile import ZipFile
from lxml import etree
z=ZipFile('UAV_Traffic_Safety_Interim_Report_Combined.docx')
r=etree.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
print('render breaks',len(r.xpath('.//w:lastRenderedPageBreak',namespaces=ns)))

"""Rasterize Word-exported PDFs and report page geometry for visual QA."""
from pathlib import Path
import json
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
qa=ROOT/'outputs/qa'
qa.mkdir(exist_ok=True)
summary=[]
for path in sorted((ROOT/'outputs').glob('*.pdf')):
    pdf=pymupdf.open(path)
    folder=qa/path.stem
    folder.mkdir(exist_ok=True)
    pages=[]
    for i,page in enumerate(pdf):
        text=page.get_text()
        if len(text.strip())<30:raise ValueError(f'Empty page: {path.name} {i+1}')
        image_path=folder/f'page-{i+1:02}.png'
        page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(image_path)
        spans=[span for b in page.get_text('dict')['blocks'] if 'lines' in b
               for line in b['lines'] for span in line['spans'] if span['text'].strip()]
        outside=[s['text'] for s in spans if s['bbox'][0]<35 or s['bbox'][2]>page.rect.width-35
                 or s['bbox'][1]<30 or s['bbox'][3]>page.rect.height-25]
        if outside:raise ValueError(f'Content outside review bounds: {path.name} {i+1}: {outside}')
        pages.append({'page':i+1,'characters':len(text),'image':image_path.name})
    summary.append({'file':path.name,'pages':len(pdf),'bookmarks':len(pdf.get_toc()),'page_checks':pages})
    print(path.name,len(pdf),'pages')
(qa/'render-summary.json').write_text(json.dumps(summary,indent=2))

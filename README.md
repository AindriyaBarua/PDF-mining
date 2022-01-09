# PDF-mining

I was given about 600 PDF files of various formats and sources, and a CSV file bse_companies.csv that had names of about 7000 Indian companies.

Goal:
1. Go through each PDF file, extract names of the authors of the document.
2. extract the institution that authored this document, e.g., Kotak Equitiies Research, ICICI securities etc. In certain cases there will be no institution associated with the document, in that case mark it as "Others".
3. Extract the names of companies mentioned in each PDF.
4. If it is a company report, then get the broker recommendation - BUY/SELL etc
5. If it is a company report, get the Target Price of the stock.

Approach:

1. Extracted pagewise text from PDF files with pdfminer
2. Built Indian data of companies and names, finetuned dislim/BERT-based-NER with Indian data
3. Trained NER model to recognise ORG, PER, used it for Goals 1, 2, 3
4. Used fasttext with weighted words from text and title as seperate features and used it with unsupervised KNN clustering to identfify reports
5. Used regex on reports classified to get Goals 4, 5

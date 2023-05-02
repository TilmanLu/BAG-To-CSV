# BAG-To-CSV

This is a Python script that scrapes the website of the German Federal Labour Court 
(Bundesarbeitsgericht) and extracts key information from its PDF decisions and converts them into 
TXT files. The User can input how many pages of the website shall be scraped; each page contains 50 
decisions. The TXT files are saved in a folder with the corresponding name of the PDF file. For 
example, the PDF file "BAG 12.12.2021.pdf" will be saved as a TXT file in a folder called "BAG 
12.12.2021". The script also saves the relevant information from each decision in a CSV file with 
columns such as "Gericht", "Senat", "Datum", "Entscheidungsstichworte", and "Leitsatz".

The future implications of this project are significant, as the collected data can be used for Natural 
Language Processing (NLP) and Machine Learning (ML) algorithms. With this data, the goal is to 
develop an automated system that can analyze the structure of labor law decisions and apply them to 
similar cases. This would be a significant advancement in legal technology and could greatly benefit 
lawyers, judges, and legal scholars.

# BundesArbeitsGericht (BAG) Decisions Scraping To .csv

## Requirements

This project uses the following Python libraries:
- `tkinter`
- `subprocess`
- `requests`
- `bs4`
- `fitz`
- `glob`
- `shutil`
- `csv`

To install them, use the following command:

```
pip install tkinter subprocess requests beautifulsoup4 pymupdf glob2 shutil csv
```

## Usage

To run the script, open a command prompt or terminal window, navigate to the folder where the 
script is saved, and type the following command:

```
python main.py
```

After starting the script, a window will open in which you can enter how many pages of the website 
you want to scrape for the decisions. For each page the script will scrape all 50 decisions.
After running the script, all the downloaded PDF files will be saved in a folder called "PDFs", which 
will be created in the same folder where the script is saved. The processed TXT files will be saved in a 
subfolder called "BAG Urteile processed". In the same folder as to where your python script is located 
as well as the executable after running the program you will find a .csv file with all the above-
mentioned information. This .csv file can be opened with applications such as Excel.

## Notes

This script was tested on Windows 10 and Python 3.8.5.

## License

This project is licensed under the MIT License.

Additional Information:

- This script is designed to work with the BAG decisions website and may not work with other 
websites.
- The script can only download PDF files from pages 1 to 127 of the BAG decisions website.
- The Script will download all 50 decisions present on each site.
- The script can only convert PDF files that are not password-protected.

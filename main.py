import tkinter as tk
import subprocess
import requests
from bs4 import BeautifulSoup
import fitz
import glob
import shutil
import csv
import os
#pymupdf install to make fitz work

# Get the current directory where the script is being executed
current_dir = os.getcwd()

# Define the source directory path
source_dir = current_dir

# Define the destination directory path
destination_dir = os.path.join(current_dir, "BAG Urteile processed")

# Check if the destination directory exists, and create it if it doesn't
if not os.path.exists(destination_dir):
    os.mkdir(destination_dir)

# Define the pdf directory path
pdf_dir = os.path.join(source_dir, "PDFs")

# Check if the destination directory exists, and create it if it doesn't
if not os.path.exists(pdf_dir):
    os.mkdir(pdf_dir)

#01 check the Entscheidungen on the BAG Website and scrape all pdfs
def bag_urteile_scrapen():

    #download pdf function
    def download_pdf(url):
        # Requests URL and get response object
        response = requests.get(url)

        # Parse text obtained
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all hyperlinks present on webpage
        links = soup.find_all('a')

        # From all links check for pdf link and
        # if present download file
        for link in links:
            if ('.pdf' in link.get('href', [])):
                print("downloading pdf")
                # Get response object for link
                response = requests.get(link.get('href'))

                filename = os.path.join(link['href'].split('/')[-1])
                # with open(filename, 'wb') as f:
                #     f.write(requests.get(urljoin(url, link['href'])).content)

                # Write content in pdf file
                pdf = open(filename + ".pdf", 'wb')
                pdf.write(response.content)
                pdf.close()
                print("writing pdf " + filename)

    # Get the number from the text field
    number_str = number_field.get()

    if not number_str or int(number_str) == 1:
        # No input given, or number == 1
        url = "https://www.bundesarbeitsgericht.de/entscheidungen/"
        download_pdf((url))
    elif int(number_str) == 2:
        url = "https://www.bundesarbeitsgericht.de/entscheidungen/"
        download_pdf((url))
        url_page_2 = "https://www.bundesarbeitsgericht.de/entscheidungen/page/" + str(2)
        download_pdf(url_page_2)
    else:
        if int(number_str) > 2 and int(number_str) <= 127:
            range_number = int(number_str)
            url = "https://www.bundesarbeitsgericht.de/entscheidungen/"
            download_pdf((url))
            for count in range(2, range_number):
                url_page_x = "https://www.bundesarbeitsgericht.de/entscheidungen/page/" + str(count)
                download_pdf(url_page_x)
        else:
            print("Number must be between 1 and 127")


    # move .pdf from working dir into pdf dir
    pdf_dir = os.path.join(source_dir, "PDFs")

    # Check if the destination directory exists, and create it if it doesn't
    if not os.path.exists(pdf_dir):
        os.mkdir(pdf_dir)

    files = os.listdir(source_dir)

    for f in files:
        if f.endswith('.pdf'):
            try:
                shutil.move(os.path.join(source_dir, f), os.path.join(pdf_dir, f))
            except FileExistsError:
                os.remove(os.path.join(pdf_dir, f))
                shutil.move(os.path.join(source_dir, f), os.path.join(pdf_dir, f))
            except Exception as e:
                print(f"An error occurred while moving {f}: {str(e)}")

    print("All pdf moved into folder.")

#02 convert those pdfs into .txt files and add the corresponding files into subfolders together
def pdf_into_txt():
    # Define the input and output directories

    new_dir = destination_dir
    log_file = os.path.join(new_dir, 'error_log.txt')

    # Make sure the output directory exists
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    # Specify the encoding for German text
    encoding = 'utf-8'

    # Create the log file
    with open(log_file, 'w', encoding=encoding) as log:
        log.write('List of PDF files that could not be opened:\n')

    # Loop through all PDF files in the pdf_dir directory
    for pdf_file in glob.glob(os.path.join(pdf_dir, '*.pdf')):
        try:
            # Open the PDF file and extract the text
            doc = fitz.open(pdf_file)
            text = ''
            for page in doc:
                text += page.get_text()
            # Close the PDF file
            doc.close()

            # Construct the name of the new subdirectory for the processed files
            new_subdir = os.path.join(new_dir, os.path.basename(pdf_file).replace('.pdf', ''))

            # Check if the directory already exists
            if not os.path.exists(new_subdir):
                # Create the new subdirectory
                os.makedirs(new_subdir)
            else:
                # If the subdirectory already exists, skip this PDF file
                print(f"Skipping {pdf_file} because {new_subdir} already exists")
                continue

            # Write the extracted text to a new file in the new subdirectory
            txt_file = os.path.join(new_subdir, os.path.basename(pdf_file).replace('.pdf', '_txt.txt'))
            with open(txt_file, 'w', encoding=encoding) as f:
                f.write(text)

            # Move the processed PDF file to the new subdirectory
            shutil.move(pdf_file, os.path.join(new_subdir, os.path.basename(pdf_file)))

        except Exception as e:
            # Log the error in the error log file with the filename of the PDF file
            with open(log_file, 'a', encoding=encoding) as log:
                log.write(f'{pdf_file} could not be processed: {str(e)}\n')
            continue

    # Move the log file to the source directory
    shutil.move(log_file, os.path.join(source_dir, os.path.basename(log_file)))

    print("ALL FINISHED")

#03 crawl all .txt files for the information wanted for the .csv
def txt_file_into_csv():

    root_dir = destination_dir
    output_file = os.path.join(root_dir, 'BAG Urteile.csv')

    # Check if output file exists and read existing "Aktenzeichen" values into a set
    existing_aktenzeichen = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header row
            for row in reader:
                existing_aktenzeichen.add(row[3])

    # Create the output file
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Check if header row has already been written
        header_written = False
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            header_written = True

        # Write the header row
        if header_written == False:
            writer.writerow(['GERICHT', 'DATUM', 'SENAT', 'AKTENZEICHEN', 'ENTSCHEIDUNGSSTICHWORTE', 'LEITSATZ'])

        # Loop through all subdirectories in the root directory
        for subdir, dirs, files in os.walk(root_dir):
            # Loop through all files in the subdirectory
            for file in files:
                # Check if the file is a text file
                if file.endswith('.txt'):
                    # Open the file and extract the relevant information
                    with open(os.path.join(subdir, file), 'r', encoding='utf-8') as txt_file:
                        try:
                            # Read the lines of the text file
                            lines = txt_file.readlines()

                            # Extract the relevant information
                            gericht = lines[0].strip()
                            datum = lines[1].strip()
                            senat = lines[2].strip()
                            aktenzeichen = lines[3].strip()

                            # Check if Aktenzeichen already exists in the CSV file
                            if aktenzeichen in existing_aktenzeichen:
                                continue

                            # Initialize variables for Entscheidungsstichworte and Leitsatz
                            entscheidungsstichworte = ''
                            leitsatz = ''

                            entscheidungsstichworte = ""
                            for i, line in enumerate(lines):
                                if line.startswith('Entscheidungsstichworte:'):
                                    j = i + 1
                                    while j < len(lines) and ':' not in lines[j]:
                                        entscheidungsstichworte += lines[j].strip()
                                        j += 1
                                    break

                            leitsatz = ""
                            for i, line in enumerate(lines):
                                if line.startswith('Leitsatz'):
                                    j = i + 1
                                    while j < len(lines) and 'ECLI' not in lines[j]:
                                        leitsatz += lines[j].strip()
                                        j += 1
                                    break

                            # Replace umlauts in the "Entscheidungsstichworte" and "Leitsatz" columns
                            entscheidungsstichworte = entscheidungsstichworte.replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue').replace('ä', 'ae').replace('ö', 'oe').replace('ü',
                                                                                                                            'ue')
                            leitsatz = leitsatz.replace("§", "PARAGRAPH ").replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue').replace('ä', 'ae').replace('ö', 'oe').replace('ü',
                                                                                                                            'ue')

                            senat = senat.replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue').replace('ä', 'ae').replace('ö', 'oe').replace('ü',
                                                                                                                            'ue')

                            # Write the extracted information to the output file
                            writer.writerow([gericht, datum, senat, aktenzeichen, entscheidungsstichworte, leitsatz])


                        except IndexError as e:
                            # Log the error to a text file in the "processed" folder
                            error_log_file = os.path.join(source_dir, 'Error Log.txt')
                            with open(error_log_file, 'a', encoding='utf-8') as error_file:
                                error_file.write(f'Error in file {os.path.join(subdir, file)}: {e}\n')
                            # Print the error message to console
                            print(f'Error in file {os.path.join(subdir, file)}: {e}')

    print("Finished creating .cvs File!")

#04 additionally add all .txt into one big .txt for future projects with ML Algorithms
def add_all_txt_into_one():

    root_dir = destination_dir
    output_dir = source_dir
    output_file = os.path.join(output_dir, 'BAG Urteile_gesamt.txt')

    # Loop through all subdirectories in the root directory
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for subdir, dirs, files in os.walk(root_dir):
            # Loop through all files in the subdirectory
            for file in files:
                # Check if the file is a text file
                if file.endswith('.txt'):
                    # Open the file and extract the relevant information
                    with open(os.path.join(subdir, file), 'r', encoding='utf-8') as txt_file:
                        # Read the lines of the text file
                        lines = txt_file.readlines()

                        # Replace ÄÖÜäöü with AOUaou and § with Paragraph
                        for i in range(len(lines)):
                            lines[i] = lines[i].replace("Ä", "A").replace("Ö", "O").replace("Ü", "U").replace("ä",
                                                                                                              "a").replace(
                                "ö", "o").replace("ü", "u").replace("§", "PARAGRAPH ")

                        # Write the current file's lines to the output file
                        out_file.writelines(lines)

                        # Write a blank line after each file
                        out_file.write('\n')

    print(f"All processed files have been concatenated into {output_file}.")

# Function that runs after the button click // runs all above functions as well
def run_code():

    # run all functions
    bag_urteile_scrapen()
    pdf_into_txt()
    txt_file_into_csv() #open .csv in excel doesnt work
    add_all_txt_into_one()

    # Define CSV file name
    csv_filename = "BAG Urteile.csv"

    # Define full path of the CSV file
    csv_file_path = os.path.join(destination_dir, csv_filename)

    # Check if the CSV file exists
    if os.path.isfile(csv_file_path):
        # Open the CSV file using the excel
        excel_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.exe"
        subprocess.call([excel_path, csv_file_path], shell=True)
    else:
        print("The CSV file does not exist.")

    #move .csv file to source dir
    shutil.move(f"{destination_dir}/{csv_filename}", f"{source_dir}/{csv_filename}")

# Create the main window
root = tk.Tk()
root.geometry("400x300")
root.title("BAG Entscheidungen")
root.configure(bg="#2d3436")

# Add a label to the window
label = tk.Label(root, text="Der Button lädt alle BAG Urteile herunter,\n für die Anzahl an Seiten,\n die du hier unten eingibst.",
                 font=("Helvetica", 14), fg="#dfe6e9", bg="#2d3436")
label.pack(pady=20)

# Add a label to the window
label1 = tk.Label(root, text="Gib eine Zahl von 1 - 127 ein.\n Das lädt die Anzahl von Urteilen x 50", font=("Helvetica", 12), fg="#dfe6e9", bg="#2d3436")
label1.pack(pady=5)

# Add a text field to the window
number_field = tk.Entry(root, font=("Helvetica", 12), bg="#dfe6e9", fg="#2d3436", justify="center")
number_field.pack(pady=10)

# Add a button to the window
button = tk.Button(root, text="Run", font=("Helvetica", 12), fg="#dfe6e9", bg="#0984e3", command=run_code)
button.pack()

# Run the main loop
root.mainloop()

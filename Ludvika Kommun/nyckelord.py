#Stefan Sommarsjö 2024
#https://github.com/sestsom
#Nyckelord söker igenom filerna nedladdade med Sluk efter nyckelord och summerar med en html sida

import os
import re
import fitz  
import sys

#Folder där filerna ligger
root_directory = "filer"

#Nyckelord att söka efter
keywords = [r'Guldläge(t)?', r'Sporthall(en)?', r'Idrottshall(en)?', 'Neuropsykiatrisk', 'NPF', 'Koordinator', 'Detaljplan', 'Hillängen', 'Granat']

#Skapa en dictionary för att lagra resultat som vi ska skriva till HTML-tabell
results = {keyword: [] for keyword in keywords}

#Variabler för felaktiga dokument och felaktiga filnamn
total_documents_scanned = 0
failed_documents = 0
failed_files = []

#Finputsa för summering
def format_keyword(keyword):
    keyword = keyword.replace(r'(t)?', 't')  # Byter ut (t)? mot t
    keyword = keyword.replace(r'(en)?', 'en')  # Byter ut (en)? mot en
    return keyword

#Söka nyckelord i en pdf filer
def search_keyword_in_pdf(filepath, keywords):
    global total_documents_scanned, failed_documents, failed_files
    try:
        doc = fitz.open(filepath)
        total_documents_scanned += 1
        text = ""
        for page in doc:
            text += page.get_text()

        #Debugga lite
        print(f"Extraherad text från {filepath}: {text[:10]}...")

        #Spara för att undvika dubbletter
        seen_snippets = set()

        #Viktig ändring: Sök varje keyword oberoende för varje dokument
        for keyword in keywords:
            #Använd re.IGNORECASE för guds skull
            matches = re.findall(rf'\b{keyword}\b', text, re.IGNORECASE)
            if matches:
                relative_filepath = os.path.relpath(filepath, start=root_directory)
                relative_filepath = f"filer/{relative_filepath.replace('\\', '/')}"
                
                #Hämta filnamnet
                file_name = os.path.basename(filepath)

                #Visa kontext
                for match in re.finditer(rf'.{{0,500}}\b{keyword}\b.{{0,500}}', text, re.IGNORECASE):  # 500 tecken före och efter
                    snippet = f"...{match.group(0)}..."
                    
                    #Redan har lagts till för just detta nyckelord?
                    if snippet not in seen_snippets:
                        seen_snippets.add(snippet)
                        #Lägg till dokumentet i alla matchande nyckelord
                        results[keyword].append((snippet, file_name, relative_filepath))
    except fitz.fitz.Error as e:
        print(f"MuPDF fel i {filepath}: {e}")
        failed_documents += 1
        failed_files.append(filepath)
    except Exception as e:
        print(f"Problem med {filepath}: {e}")
        failed_documents += 1
        failed_files.append(filepath)

#Rekursiv sök
def search_in_all_pdfs(directory, keywords):
    total_files = sum([len(files) for r, d, files in os.walk(directory)])
    processed_files = 0

    try:
        for subdir, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".pdf"):
                    filepath = os.path.join(subdir, file)
                    print(f"Processar {filepath} ({processed_files + 1}/{total_files})...")
                    search_keyword_in_pdf(filepath, keywords)
                    processed_files += 1

    except KeyboardInterrupt:
        print("\nAvslutar...")
        sys.exit(0)
#Kör
try:
    search_in_all_pdfs(root_directory, keywords)
except KeyboardInterrupt:
    print("\nOk, avslutar...")
    sys.exit(0)

#Skapa en summering
html_content = f"""
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Summering av nyckelord</title>
    <style>
        body {{ font-family: Calibri, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ cursor: pointer; color: #1a73e8; text-decoration: underline; }}
        .hidden {{ display: none; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
        a {{ color: #1a73e8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
    <script>
        function toggleVisibility(id) {{
            var element = document.getElementById(id);
            if (element.classList.contains('hidden')) {{
                element.classList.remove('hidden');
            }} else {{
                element.classList.add('hidden');
            }}
        }}
    </script>
</head>
<body>
    <h1>Summering av nyckelord</h1>
    <p>Totalt antal genomsökta dokument: {total_documents_scanned}</p>
    <p>Antal dokument med fel: <a href="#" onclick="toggleVisibility('failed')">{failed_documents}</a></p>

    <div id="failed" class="hidden">
        <h2>Dokument som innehåller något fel</h2>
        <ul>
"""

#Lägg till varje fil med fel i listan
for file in failed_files:
    html_content += f"<li>{file}</li>"

html_content += """
        </ul>
    </div>
"""

#Lägg till resultaten
for keyword, matches in results.items():
    formatted_keyword = format_keyword(keyword)
    count = len(matches)
    html_content += f"""
    <h2 onclick="toggleVisibility('{formatted_keyword}')">{formatted_keyword} ({count})</h2>
    <div id="{formatted_keyword}" class="hidden">
        <table>
            <tr>
                <th>Utdrag</th>
                <th>Filnamn</th>
                <th>Länk</th>
            </tr>
    """
    for snippet, file_name, link in matches:
        html_content += f"""
            <tr>
                <td>{snippet}</td>
                <td>{file_name}</td>
                <td><a href="{link}" target="_blank">Öppna PDF</a></td>
            </tr>
        """
    html_content += """
        </table>
    </div>
    """

html_content += """
</body>
</html>
"""

#Skriv
with open("summering.html", "w", encoding="utf-8") as html_file:
    html_file.write(html_content)

print("\nSökningen är klar. Resultaten har sparats i 'summering.html'.")

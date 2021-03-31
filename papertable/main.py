# %%
import os

import bibtexparser
import pandas as pd
import requests

import papertable as pt

# Download Sciwheel references
headers = {"Authorization": "Bearer {}".format(os.getenv("SCIWHEEL"))}
data = requests.get(
    "https://sciwheel.com/extapi/work/references/export?projectId=499895",
    headers=headers,
)

print(data.text, file=open(pt.external_dir() / "refs.bib", "w"))

# Sort table
df = pd.read_csv(pt.external_dir() / "table.csv")
df = df.groupby(["Task", "Techniques", "Domain"]).first()
df.to_csv(pt.external_dir() / "table.csv")

# Generate table html
html_string = """
<html>
  <link rel="stylesheet" type="text/css" href="{stylecss}"/>
  <body>
    <div class="container">
        <div class="fixed">
            <span style="font-size:30pt">Topics</span>
            {table}
        </div>
        <div class="flex-item">
            <span style="font-size:30pt">References</span>
            {tablerefs}
        </div>
    </div>
  </body>
</html>.
"""

# Get references
remove_keywords = [
    i
    for i in open(pt.external_dir() / "refs.bib", "r").readlines()
    if "pages = " not in i
    and "url = " not in i
    and "issn = " not in i
    and "isbn = " not in i
    and "doi = " not in i
    and "abstract = " not in i
    and "address = " not in i
    and "month = " not in i
    and "day = " not in i
    and "editor = " not in i
    and "series = " not in i
    and "volume = " not in i
    and "sciwheel-projects = " not in i
]
for i in range(len(remove_keywords)):
    if "keywords" in remove_keywords[i]:
        remove_keywords[i] = remove_keywords[i].replace(" and ", ", ")
print("".join(remove_keywords), file=open(pt.interim_dir() / "bib_nokw.bib", "w"))
bib = ["@" + i for i in open(pt.interim_dir() / "bib_nokw.bib", "r").read().split("@")]
refs = [i for i in df.References.tolist() if "_" in i]
single_refs = []
final_bib = []
for ref in refs:
    if ref.count("_") == 0:
        continue
    if ref.count("_") == 1:
        single_refs.append(ref)
    else:
        single_refs += ref.split(", ")
for b in bib:
    name = b.split(",")[0].split("{")[-1]
    if name in single_refs:
        final_bib.append(b)
str_bib = "".join(final_bib)
print(str_bib, file=open(pt.interim_dir() / "rel_bib.bib", "w"))

# Render references
with open(pt.interim_dir() / "rel_bib.bib") as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)
df_refs = pd.DataFrame(bib_database.entries)[
    ["ID", "title", "keywords", "year"]
].sort_values("ID")


# OUTPUT AN HTML FILE
with open(pt.outputs_dir() / "table.html", "w") as f:
    f.write(
        html_string.format(
            stylecss=pt.external_dir() / "df_style.css",
            table=df.to_html(classes="mystyle"),
            tablerefs=df_refs.set_index("ID").to_html(classes="mystyle"),
        )
    )

# %%

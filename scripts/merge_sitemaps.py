import xml.etree.ElementTree as ET
from pathlib import Path

# Input files
quarto_sitemap = Path("_site/sitemap.xml")
jekyll_sitemap = Path("classic/sitemap-classic.xml")

# Output file
merged_sitemap = Path("site/sitemap.xml")

# Load and parse both
def extract_urls(path):
    tree = ET.parse(path)
    return list(tree.getroot())

quarto_urls = extract_urls(quarto_sitemap)
jekyll_urls = extract_urls(jekyll_sitemap)

# Merge
urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
for url in quarto_urls + jekyll_urls:
    urlset.append(url)

# Write merged sitemap
ET.ElementTree(urlset).write(merged_sitemap, encoding="utf-8", xml_declaration=True)

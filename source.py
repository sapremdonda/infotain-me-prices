"""Official retail prices for the four metros, from PPAC (Petroleum Planning & Analysis Cell,
Ministry of Petroleum and Natural Gas). PPAC posts a daily PDF with petrol and diesel prices for
Delhi, Mumbai, Chennai and Kolkata; this reads its newest row.
"""
import datetime
import re
import subprocess
import tempfile
import urllib.request

PAGE = "https://ppac.gov.in/retail-selling-price-rsp-of-petrol-diesel-and-domestic-lpg/rsp-of-petrol-and-diesel-in-metro-cities-since-16-6-2017"
AGENT = "Mozilla/5.0 (compatible; daily-fuel-price-file/1)"

# Column order in the PDF.
METROS = [
    {"city": "Delhi", "state": "Delhi", "aliases": ["New Delhi"]},
    {"city": "Mumbai", "state": "Maharashtra", "aliases": ["Bombay"]},
    {"city": "Chennai", "state": "Tamil Nadu", "aliases": ["Madras"]},
    {"city": "Kolkata", "state": "West Bengal", "aliases": ["Calcutta"]},
]

DATE = r"(\d{1,2}-[A-Za-z]{3}-\d{2})"
NUM = r"(\d{2,3}\.\d{2})"
ROW = re.compile(r"^\s*" + DATE + r"\s+" + r"\s+".join([NUM] * 4) + r"\s+" + DATE + r"\s+" + r"\s+".join([NUM] * 4), re.M)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def pdf_url(html):
    links = re.findall(r'["\']([^"\']*DailyPriceMSHSD_Metro[^"\']*\.pdf)["\']', html)
    if not links:
        raise RuntimeError("No daily metro price PDF linked on the PPAC page")
    link = links[0]
    return link if link.startswith("http") else "https://ppac.gov.in" + ("" if link.startswith("/") else "/") + link


def parse(text):
    """Returns (date, places) from the PDF's text (pdftotext -layout)."""
    m = ROW.search(text)
    if not m:
        raise RuntimeError("Couldn't find a price row in the PDF")
    g = m.groups()
    day = datetime.datetime.strptime(g[0], "%d-%b-%y").date()
    if datetime.datetime.strptime(g[5], "%d-%b-%y").date() != day:
        raise RuntimeError("Petrol and diesel rows have different dates")
    petrol, diesel = g[1:5], g[6:10]
    places = [dict(m, petrol=float(p), diesel=float(d), cng=None) for m, p, d in zip(METROS, petrol, diesel)]
    return day, places


def fetch():
    html = get(PAGE).decode("utf-8", "replace")
    pdf = get(pdf_url(html))
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(pdf)
        f.flush()
        text = subprocess.run(["pdftotext", "-layout", f.name, "-"], check=True, capture_output=True, text=True).stdout
    return parse(text)

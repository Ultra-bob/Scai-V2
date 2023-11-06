import requests
from pathlib import Path

r = requests.get(
    "https://starcitizen.tools/api.php?action=parse&page=A1%20Spirit&prop=text&format=json"
)

Path("test.html").write_text(r.json()["parse"]["text"]["*"])
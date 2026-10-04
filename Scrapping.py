import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

ROOT = 'https://news.kompas.com/?source=navbar'

PARAMS = {'site': 'all', 'date': '2026-10-03'}
MAX_PAGE = 5
DELAY = 1
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/124.0 Safari/537.36')
}

def parse_page(html):
    """Mengambil semua berita dari satu halaman HTML, mengembalikan list of dict."""
    soup = BeautifulSoup(html, 'html.parser')

    items = soup.find_all('div', {'class': 'articleItem'})

    hasil = []
    for item in items:
        tag_a = item.find('a', href=True)
        tag_judul = item.find('h2', {'class': 'articleTitle'})
        tag_kategori = item.find('div', {'class': 'articlePost-subtitle'})
        tag_tanggal = item.find('div', {'class': 'articlePost-date'})
        
        hasil.append({
            'Judul'   : tag_judul.get_text(strip=True) if tag_judul else None,
            'Kategori': tag_kategori.get_text(strip=True) if tag_kategori else None,
            'Link'    : tag_a['href'] if tag_a else None,
            'Tanggal' : tag_tanggal.get_text(strip=True) if tag_tanggal else None,
        })
    return hasil

data_berita = []   

for page in range(1, MAX_PAGE + 1):
    params = {**PARAMS, 'page': page}

    try:
        resp = requests.get(ROOT, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()  
    except requests.RequestException as e:
        print(f'Halaman {page} gagal diambil: {e}')
        break

    berita = parse_page(resp.text)

    if not berita:
        print(f'Halaman {page} kosong, scraping dihentikan.')
        break

    data_berita.extend(berita)
    print(f'Halaman {page}: {len(berita)} berita (total {len(data_berita)})')

    time.sleep(DELAY)  


df = pd.DataFrame(data_berita)

#Hapus duplikat berdasarkan link (berita yang sama bisa muncul di beberapa halaman)
df = df.drop_duplicates(subset='Link').reset_index(drop=True)

print(df.shape)
print(df.head())

df.to_csv('berita_kompas_raw.csv', index=False, encoding='utf-8-sig')

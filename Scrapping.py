#Scraping berita kompas.com: judul, kategori, link, dan tanggal terbit
#Library: requests (HTTP request), BeautifulSoup (parser HTML), pandas (tabel & CSV)

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

#=============================================================
#1. PENGATURAN
#=============================================================

#URL dasar halaman indeks berita (tanpa nomor halaman)
#Catatan: cek dulu di browser, pastikan halaman ini memang memakai struktur 'articleItem'
ROOT = 'https://news.kompas.com/?source=navbar'

#Parameter tambahan: site=all (semua kanal), date = tanggal berita yang diambil (YYYY-MM-DD)
PARAMS = {'site': 'all', 'date': '2026-10-03'}

#Jumlah halaman maksimal yang diambil
MAX_PAGE = 5

#Jeda antar request (detik) agar tidak membebani server
DELAY = 1

#Header User-Agent supaya request terlihat seperti browser biasa (mengurangi risiko diblokir)
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/124.0 Safari/537.36')
}

#=============================================================
#2. FUNGSI PARSING SATU HALAMAN
#=============================================================

def parse_page(html):
    """Mengambil semua berita dari satu halaman HTML, mengembalikan list of dict."""
    soup = BeautifulSoup(html, 'html.parser')

    #Setiap berita dibungkus <div class="articleItem">
    items = soup.find_all('div', {'class': 'articleItem'})

    hasil = []
    for item in items:
        #Link berita ada pada tag <a href="..."> yang membungkus item
        tag_a = item.find('a', href=True)
        #Judul berita ada pada <h2 class="articleTitle">
        tag_judul = item.find('h2', {'class': 'articleTitle'})
        #Kategori ada pada <div class="articlePost-subtitle">
        tag_kategori = item.find('div', {'class': 'articlePost-subtitle'})
        #Tanggal terbit ada pada <div class="articlePost-date">
        tag_tanggal = item.find('div', {'class': 'articlePost-date'})

        #Jika elemen tidak ditemukan, isi None supaya program tidak error
        hasil.append({
            'Judul'   : tag_judul.get_text(strip=True) if tag_judul else None,
            'Kategori': tag_kategori.get_text(strip=True) if tag_kategori else None,
            'Link'    : tag_a['href'] if tag_a else None,
            'Tanggal' : tag_tanggal.get_text(strip=True) if tag_tanggal else None,
        })
    return hasil

#=============================================================
#3. LOOP BEBERAPA HALAMAN
#=============================================================

data_berita = []   #penampung seluruh berita dari semua halaman

for page in range(1, MAX_PAGE + 1):
    #Gabungkan parameter tanggal/site dengan nomor halaman
    params = {**PARAMS, 'page': page}

    try:
        resp = requests.get(ROOT, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()   #lempar error jika status bukan 200 (mis. 403/404)
    except requests.RequestException as e:
        print(f'Halaman {page} gagal diambil: {e}')
        break

    berita = parse_page(resp.text)

    #Jika halaman kosong, berarti sudah habis -> hentikan loop
    if not berita:
        print(f'Halaman {page} kosong, scraping dihentikan.')
        break

    data_berita.extend(berita)
    print(f'Halaman {page}: {len(berita)} berita (total {len(data_berita)})')

    time.sleep(DELAY)   #jeda sebelum request berikutnya

#=============================================================
#4. SIMPAN KE DATAFRAME & CSV
#=============================================================

df = pd.DataFrame(data_berita)

#Hapus duplikat berdasarkan link (berita yang sama bisa muncul di beberapa halaman)
df = df.drop_duplicates(subset='Link').reset_index(drop=True)

print(df.shape)
print(df.head())

#Simpan ke CSV (utf-8-sig agar karakter tampil benar saat dibuka di Excel)
df.to_csv('berita_kompas_raw.csv', index=False, encoding='utf-8-sig')
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import folium_static, st_folium
import folium
import pandas as pd
from geopy.geocoders import ArcGIS
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import json
import os
import re
from datetime import datetime
from scipy.spatial import ConvexHull, QhullError
from folium.plugins import MarkerCluster
from fuzzywuzzy import process, fuzz
from Levenshtein import distance as levenshtein_distance
import numpy as np
from pathlib import Path
from streamlit_extras.metric_cards import style_metric_cards
from function.clustering import add_logo
import io
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from sklearn.metrics import silhouette_score
import hashlib
# Normalization map and function for school names
NORMALIZATION_MAP = {
    'NEGERI': 'N',
    'NEGRI': 'N',
    'NEGER': 'N',
    'SMK': 'SMK',
    'SEKOLAH MENENGAH KEJURUAN': 'SMK',
    'SEKOLAH MENENGAH AGAMA KATOLIK' : 'SMAK',
    'SEKOLAH MENENGAH TEOLOGI KRISTEN' : 'SMTK',
    'SEKOLAH MENENGAH ATAS TEOLOGI KRISTEN' : 'SMTK',
    'YK' : 'YOGYAKARTA',
    'SMA K PENABUR' : 'SMAS BPK PENABUR',
    'JOGJAKARTA' : 'YOGYAKARTA',
    'SATU' : '1',
    'GIRSIP' : 'GIRSANG SIPANGAN',
    'SETIA BUDI' : 'SETYA BUDI',
    'SMA Ursulin' : 'SMA REGINA PACIS',
    'PEM RAYA' : 'PAMATANG RAYA',
    'SMAN 1 WAREN' : 'SMAN WAREN',
    'PANGUDILUHUR' : 'PANGUDI LUHUR',
    'PL' : 'PANGUDI LUHUR',
    'STELLADUCE' : 'STELLA DUCE',
    'KS CILEGON' : 'KRAKATAU STEEL CILEGON',
    'YESU' : 'JESU',
    'STM' : 'SMK',
    'KLAUSE' : 'KLAUS',
    'SANTU' : 'SANTO',
    'SMA YPPK ASISI JAYAPURA PAPUA' : 'SMA YPPK ASISI SENTANI',
    'Saverius' : 'XAVERIUS',
    'KAB TANGERANG' : 'TANGERANG',
    'SMK ST IGNATIUS LOYOLA' : 'SMAS ST IGNATIUS LOYOLA',
    'TIGARAJA' : 'TIGA RAJA',
    'TIGARA' : 'TIGA RAJA',
    'SMA PELAYARAN AMPARI MARAUKE' : 'SMKS AMPARI MERAUKE',
    'SMA KRISTEN 5 KLATEN' : 'SMKS KRISTEN 5 KLATEN',
    'ST' : 'SANTO',
    'EKLESIA JAILOLO' : 'EKLESIA AKEDIRI',
    'SMA DIRGANTARA PUTRA BANGSA' : 'SMKS DIRGANTARA PUTRA BANGSA',
    'SEKOLAH DARMA YUDHA' : 'SMAS DARMA YUDHA',
    'SMAN 3 MODEL SORONG' : 'SMAN 3 SORONG',
    'SMA STELLA DUCE 1 BAMBANGLIPURO' : 'SMA STELLA DUCE BAMBANGLIPURO',
    'SENIOR HIGHSCHOOL' : 'SMA',
    'SMA PANGUDI LUHUR SANTO VINCENTIUS' : 'SMA PANGUDI LUHUR SANTO VINCENTIUS GIRIWOYO',
    'SMAKr' : 'SMAS',
    'SMK TI PRAMATAM' : 'SMK TI PRATAMA',
    'DUA' : '2',
    'Telkom' : 'TELEKOMUNIKASI',
    'SMK TELEKOMUNIKASI MEDAN' : 'SMK TELEKOMUNIKASI 1 MEDAN',
    'SMA SW BANDAR BARU' : 'SMAS RK DELI MURNI SIBOLANGIT',
    'CHANDRA WIDYA' : 'CANDRA WIDYA',
    'SMKN 1 MASOHI' : 'SMKN 1 Maluku Tengah',
    'SMA Ursulin Surakarta' : 'SMA REGINA PACIS SURAKARTA',
    'SMKN 3 JAYAPURA' : 'SMKN 3 Teknologi Dan Rekayasa Kota Jayapura',
    'SMA HKBP PEMATANG SIANTAR' : 'SMAS HKBP 1',
    'Bhina Khusma' : 'Bina Kusuma',
    'HALTIM' : 'HALMAHERA TIMUR',
    'HALUT' : 'HALMAHERA UTARA',
    'SMA THERESIA 1 SEMARANG' : 'SMA THERESIANA 1 SEMARANG',
    'SMAN TAMIANG LAYANG' : 'SMAN 1 TAMIANG LAYANG',
    'SMAN 5 ANGKASA' : 'SMAN 5 JAYAPURA',
    'SMAN 9 BIMBINGAN KHUSUS' : 'SMAN 9 MANADO',
    'SMK MUHAMMADIYAH SERUI' : 'SMKS MUHAMMADIYAH TEKNOLOGI DAN REKAYASA SERUI',
    'SMKS KATOLIK TUNAS BANGSA' : 'SMKS TUNAS BANGSA',
    'SMA SANTO ALOYSIUS 1' : 'SMA ALLOYSIUS 1',
}



# Data referensi program studi
prodi_reference = {
    "01": "Filsafat Keilahian",
    "11": "Manajemen",
    "12": "Akuntansi",
    "13": "Magister Manajemen",
    "21": "Arsitektur",
    "22": "Informatika",
    "23": "Sistem Informasi",
    "24": "Desain Produk",
    "31": "Biologi",
    "41": "Pendidikan Dokter",
    "50": "Magister Filsafat Keilahian",
    "57": "S3 Ilmu Teologi",
    "59": "Matrikulasi Filsafat Keilahian",
    "63": "Magister Arsitektur",
    "81": "Pendidikan Bahasa Inggris",
    "82": "Studi Humanitas",
}

# Normalization map for provinces
PROVINCE_NORMALIZATION_MAP = {
    'D.K.I Jakarta': 'Prov. D.K.I. Jakarta',
    'D.I. Yogyakarta': 'Prov. D.I. Yogyakarta',
    'Bali': 'Prov. Bali',
    'Bangka Belitung': 'Prov. Kepulauan Bangka Belitung',
    'Banten': 'Prov. Banten',
    'Bengkulu': 'Prov. Bengkulu',
    'D.I. Aceh': 'Prov. Aceh',
    'Gorontalo': 'Prov. Gorontalo',
    'Jambi': 'Prov. Jambi',
    'Jawa Barat': 'Prov. Jawa Barat',
    'Jawa Tengah': 'Prov. Jawa Tengah',
    'Jawa Timur': 'Prov. Jawa Timur',
    'Kalimantan Barat': 'Prov. Kalimantan Barat',
    'Kalimantan Selatan': 'Prov. Kalimantan Selatan',
    'Kalimantan Tengah': 'Prov. Kalimantan Tengah',
    'Kalimantan Timur': 'Prov. Kalimantan Timur',
    'Kalimantan Utara': 'Prov. Kalimantan Utara',
    'Riau': 'Prov. Riau',
    'Lampung': 'Prov. Lampung',
    'Maluku': 'Prov. Maluku',
    'Maluku Utara': 'Prov. Maluku Utara',
    'Nusa Tenggara Barat': 'Prov. Nusa Tenggara Barat',
    'Nusa Tenggara Timur': 'Prov. Nusa Tenggara Timur',
    'Papua Barat': 'Prov. Papua Barat',
    'Papua Timur': 'Prov. Papua Timur',
    'Prov Kepulauan Riau': 'Prov. Kepulauan Riau',
    'Kepulauan Riau': 'Prov. Kepulauan Riau',
    'Prov. Papua': 'Prov. Papua',
    'Papua' : 'Prov. Papua',
    'Sulawesi Barat': 'Prov. Sulawesi Barat',
    'Sulawesi Selatan': 'Prov. Sulawesi Selatan',
    'Sulawesi Tengah': 'Prov. Sulawesi Tengah',
    'Sulawesi Tenggara': 'Prov. Sulawesi Tenggara',
    'Sulawesi Utara' : 'Prov. Sulawesi Utara',
    'Sumatra Barat': 'Prov. Sumatera Barat',
    'Sumatra Selatan': 'Prov. Sumatera Selatan',
    'Sumatra Utara': 'Prov. Sumatera Utara',
}
# Normalization map for provinces
KABUPATEN_NORMALIZATION_MAP = {
    'Kodya Yogyakarta' : 'Kota Yogyakarta',
    'Kab. Kulonprogo' : 'Kab. Kulon Progo',
    'Kab. Bantul' : 'Kab. Bantul',
    'Kab. Gunungkidul' : 'Kab. Gunung Kidul',
    'Kab. Sleman' : 'Kab. Sleman',
    'Kab. Jembrana' : 'Kab. Jembrana',
    'Kab. Tabanan': 'Kab. Tabanan',
    'Kab. Badung' : 'Kab. Badung',
    'Kab. Gianjar' : 'Kab. Gianyar',
    'Kab. Klungkung' : 'Kab. Klungkung',
    'Kab. Bangli' : 'Kab. Bangli',
    'Kab. Karangasem' : 'Kab. Karang Asem',
    'Kab. Buleleng' : 'Kab. Buleleng',
    'Kodya Denpasar' : 'Kota Denpasar',
    'Kab. Bangka' : 'Kab. Bangka',
    'Kab. Belitung' : '	Kab. Belitung',
    'Kab. Bangka Tengah' : 'Kab. Bangka Tengah	',
    'Kab. Bangka Barat' : 'Kab. Bangka Barat',
    'Kab. Bangka Selatan' : 'Kab. Bangka Selatan',
    'Kab. Belitung Timur' : 'Kab. Belitung Timur',
    'Kota Pangkal Pinang' : 'Kota Pangkalpinang',
    'Kab. Serang' : 'Kab. Serang',
    'Kab. Pandeglang' : 'Kab. Pandeglang',
    'Kab. Lebak' : 'Kab. Lebak',
    'Kab. Tangerang' : 'Kab. Tangerang',
    'Kodya Cilegon' : '	Kota Cilegon',
    'Kodya Tangerang' : 'Kota Tangerang',
    'Kota Serang' : 'Kota Serang',
    'Kota Tangerang Selatan' : 'Kota Tangerang Selatan',
    'Kab. Bengkulu Selatan' : 'Kab. Bengkulu Selatan	',
    'Kab. Rejanglebong' : 'Kab. Rejang Lebong',
    'Kab. Bengkulu Utara' : 'Kab. Bengkulu Utara',
    'Kodya Bengkulu' : 'Kota Bengkulu',
    'Kab. Muko-muko' : 'Kab. Muko-muko',
    'Kab. Kepahiang' : 'Kab. Kepahiang',
    'Kab. Lebong' : 'Kab. Lebong',
    'Kab. Kaur' : 'Kab. Kaur',
    'Kab. Seluma' : 'Kab. Seluma',
    'Kab. Bengkulu Tengah' : 'Kab. Bengkulu Tengah',
    'Kab. Aceh Selatan' : 'Kab. Aceh Selatan',
    'Kab. Aceh Tenggara' : 'Kab. Aceh Tenggara',
    'Kab. Aceh Timur' : 'Kab. Aceh Timur',
    'Kab. Aceh Tengah' : 'Kab. Aceh Tengah',
    'Kab. Aceh Barat' : 'Kab. Aceh Barat',
    'Kab. Aceh Besar' : 'Kab. Aceh Besar',
    'Kab. Piedi' : 'Kab. Pidie',
    'Kab. Aceh Utara' : 'Kab. Aceh Utara',
    'Kodya Banda Aceh' : 'Kota Banda Aceh',
    'Kodya Sabang' : 'Kota Sabang',
    'Kab. Bireuen' : 'Kab. Bireuen',
    'Kab. Simeuleu' : 'Kab. Simeulue',
    'Kab. Singkil' : 'Kab. Aceh Singkil',
    'Kab. Langsa' : 'Kota Langsa',
    'Kab. Aceh Barat Daya' : 'Kab. Aceh Barat Daya',
    'Kab. Gayo Lues' : 'Kab. Gayo Lues',
    'Kab. Aceh Jaya' : 'Kab. Aceh Jaya',
    'Kab. Nagan Raya' : 'Kab. Nagan Raya',
    'Kab. Aceh Tamiang' : 'Kab. Aceh Tamiang',
    'Kotif. Lhok Seumawe' : 'Kota Lhokseumawe',
    'Kab. Bener Meriah' : 'Kab. Bener Meriah',
    'Kab. Pidie Jaya' : 'Kab. Pidie Jaya',
    'Kota Subulussalam' : 'Kota Subulussalam',
    'Jakarta Selatan' : 'Kota Jakarta Selatan',
    'Jakarta Timur' : 'Kota Jakarta Timur',
    'Jakarta Pusat' : 'Kota Jakarta Pusat',
    'Jakarta Barat' : 'Kota Jakarta Barat',
    'Jakarta Utara' : 'Kota Jakarta Utara',
    'Kab. Kepulauan Seribu' : 'Kab. Kepulauan Seribu',
    'Kab. Boalemo' : 'Kab. Boalemo',
    'Kab. Gorontalo' : 'Kab. Gorontalo',
    'Kodya Gorontalo' : 'Kota Gorontalo',
    'Kab. Pohuwato' : 'Kab. Pohuwato',
    'Kab. Bone Bolango' : 'Kab. Bone Bolango',
    'Kab. Gorontalo Utara' : 'Kab. Gorontalo Utara',
    'Kab. Kerinci' : 'Kab. Kerinci',
    'Kab. B. Sarulangun' : 'Kab. Sarolangun',
    'Kab. Batanghari' : 'Kab. Batang Hari',
    'Kab. Tanujung Jagung' : 'Kab. Tanujung Jagung',
    'Kab. Muara Bungotebo' : 'Kab. Muara Bungotebo',
    'Kab. Jambi' : 'Kab. Jambi',
    'Kodya Jambi' : 'Kota Jambi',
    'Kab. Bungo' : 'Kab. Bungo',
    'Kab. Merangin' : 'Kab. Merangin',
    'Kab. Muaro Jambi' : 'Kab. Muaro Jambi',
    'Tanjung Jabung Barat' : 'Kab. Tanjung Jabung Barat',
    'Tanjung Jabung Timur' : 'Kab. Tanjung Jabung Timur',
    'Kab. Tebo' : 'Kab. Tebo',
    'Kab. Tanggamus' : 'Kab. Tanggamus',
    'Kab. Sarolangun' : 'Kab. Sarolangun',
    'Kota. Sungai Penuh' : 'Kota Sungai Penuh',
    'Kab. Bogor' : 'Kab. Bogor',
    'Kab. Sukabumi' : 'Kab. Sukabumi',
    'Kab. Cianjur' : 'Kab. Cianjur',
    'Kab. Bandung' : 'Kab. Bandung',
    'Kab. Garut' : 'Kab. Garut',
    'Kab. Tasikmalaya' : 'Kab. Tasikmalaya',
    'Kab. Ciamis' : 'Kab. Ciamis',
    'Kab. Kuningan' : 'Kab. Kuningan',
    'Kab. Cirebon' : 'Kab. Cirebon',
    'Kab. Majalengka' : 'Kab. Majalengka',
    'Kab. Sumedang' : 'Kab. Sumedang',
    'Kab. Indramayu' : 'Kab. Indramayu',
    'Kab. Subang' : 'Kab. Subang',
    'Kab. Purwakarta' : 'Kab. Purwakarta',
    'Kab. Karawang' : 'Kab. Karawang',
    'Kab. Bekasi' : 'Kab. Bekasi',
    'Kab. Serang' : 'Kab. Serang',
    'Kodya Bogor' : 'Kota Bogor',
    'Kodya Sukabumi' : 'Kota Sukabumi',
    'Kodya Bandung' : 'Kota Bandung',
    'Kodya Cirebon' : 'Kota Cirebon',
    'Kodya Depok' : 'Kota Depok',
    'Kotif. Banjar' : 'Kota Banjar',
    'Kab. Bandung Barat' : 'Kab. Bandung Barat',
    'Kota Bekasi' : 'Kota Bekasi',
    'Kota Cimahi' : 'Kota Cimahi',
    'Kota Tasikmalaya' : 'Kota Tasikmalaya',
    'Kab. Pangandaran' : 'Kab. Pangandaran',
    'Kab. Cilacap' : 'Kab. Cilacap',
    'Kab. Banyumas' : 'Kab. Banyumas',
    'Kab. Purbalingga' : 'Kab. Purbalingga',
    'Kab. Banjarnegara' : 'Kab. Banjarnegara',
    'Kab. Kebumen' : 'Kab. Kebumen',
    'Kab. Purworejo' : 'Kab. Purworejo',
    'Kab. Wonosobo' : 'Kab. Wonosobo',
    'Kab. Magelang' : 'Kab. Magelang',
    'Kab. Boyolali' : 'Kab. Boyolali',
    'Kab. Klaten' : 'Kab. Klaten',
    'Kab. Sukoharjo' : 'Kab. Sukoharjo',
    'Kab. Wonogiri' : 'Kab. Wonogiri',
    'Kab. Karanganyar' : 'Kab. Karanganyar',
    'Kodya Magelang' : 'Kota Magelang',
    'Kodya Surakarta' : 'Kota Surakarta',
    'Kodya Salatiga' : 'Kota Salatiga',
    'Kodya Semarang' : 'Kota Semarang',
    'Kodya Pekalongan' : 'Kota Pekalongan',
    'Kodya Tegal' : 'Kota Tegal',
    'Kodya Kediri' : 'Kota Kediri',
    'Kodya Blitar' : 'Kota Blitar',
    'Kodya Malang' : 'Kota Malang',
    'Kodya Probolinggo' : 'Kota Probolinggo',
    'Kodya Pasuruan' : 'Kota Pasuruan',
    'Kodya Mojokerto' : 'Kota Mojokerto',
    'Kodya Madiun' : 'Kota Madiun',
    'Kodya Surabaya' : 'Kota Surabaya',
    'Kodya Pontianak' : 'Kota Pontianak',
    'Kab. Taman Laut' : 'Kab. Tanah Laut',
    'Kab. Kota Baru' : 'Kab. Kotabaru',
    'Kab. Tapin/Tapian' : 'Kab. Tapin',
    'Kab. Hulu Sei Selatan' : 'Kab. Hulu Sungai Selatan',
    'Kab. Hulu Sei Tengah' : 'Kab. Hulu Sungai Tengah',
    'Kab. Hulu Sei Utara' : 'Kab. Hulu Sungai Utara',
    'Kodya Banjarmasin' : 'Kota Banjarmasin',
    'Kab. Kota Waringin Barat' : 'Kab. Kotawaringin Barat',
    'Kab. Kota Waringin Timur' : 'Kab. Kotawaringin Timur',
    'Kodya Palangkaraya' : 'Kota Palangka Raya',
    'Kab. Pasir' : 'Kab. Paser',
    'Kodya Balikpapan' : 'Kota Balikpapan',
    'Kodya Samarinda' : 'Kota Samarinda',
    'Kab. Penajam Paser Utr' : 'Kab. Penajam Paser Utara',
    'Kodya Bontang' : 'Kota Bontang',
    'Kodya Tarakan' : 'Kota Tarakan',
    'Kab. Mahakam Ulu' : 'Kab. Mahakam Ulu',
    'Kodya Bandar Lampung' : 'Kota Bandar Lampung',
    'Kodya Metro' : 'Kota Metro',
    'Kodya Ambon' : 'Kota Ambon',
    'Kab. Maluku Teng Barat' : 'Kab. Kepulauan Tanimbar',
    'Kab.Kepulauan Tanimbar' : 'Kab. Kepulauan Tanimbar',
    'Kab. Pulau Sula' : 'Kab. Kepulauan Sula',
    'Kab. Halmahera Utara' : 'Kab. halmahera Utara',
    'Pulau Taliabu' : 'Kab. Pulau Taliabu',
    'Kab. Mataram' : 'Kota Mataram',
    'Kab. Ngade' : 'Kab. Ngada',
    'Kodya Kupang' : 'Kota Kupang',
    'Kab. Rote-Ndao' : 'Kab. Rote-Ndao',
    'Kab. Sabu Raijua' : 'Kab. Sabu Raijua',
    'Kab. Fak Fak' : 'Kab. Fak-Fak',
    'Kab. Kep. Raja Ampat' : 'Kab. Raja Ampat',
    'Kab. Jaya Pura' : 'Kab. Jayapura',
    'Kab. Jaya Wijaya' : 'Kab. Jayawijaya',
    'Kab. Puncak jaya' : 'Kab. Puncak Jaya',
    'Kodya Jaya Pura' : 'Kota Jayapura',
    'Kab. natuna' : 'Kab. Natuna',
    'Kab. Kep. Anambas' : 'Kab. Kepulauan Anambas',
    'Kota tanjung Pinang' : 'Kota Tanjungpinang',
    'Kab. Biak Namfor' : 'Kab. Biak Numfor',
    'Kab. Yapen Waropen' : 'Kab. Kepulauan Yapen',
    'Kab. Memberamo Raya' : 'Kab. Memberamo Raya',
    'Kab. Nduga Tengah' : 'Kab. Nduga',
    'Kab. Mamberamo Tengah' : 'Kab. Mamberamo Tengah',
    'Kab. Indragiri Ulu' : 'Kab. Indragiri Hulu', 
    'Kab. Indragiri Ilir' : 'Kab. Indragiri Hilir', 
    'Kodya Pekan Baru' : 'Kota Pekanbaru', 
    'Kodya Batam' : 'Kota Batam', 
    'Kab. Kuantan Singingi' : 'Kab. Kuantan Singingi', 
    'Kab. Rokan Hilir' : 'Kab. Rokan Hilir', 
    'Kab. Rolan Hulu' : 'Kab. Rokan Hulu', 
    'Kab. Kota Batam' : 'Kota Batam', 
    'Kodya Dumai' : 'Kota Dumai', 
    'Kodya Tanjung Pinang' : 'Kota Tanjungpinang', 
    'Kab. Kep. Meranti' : 'Kab. Kepulauan Meranti',
    'Kab. Mamuju Utara': 'Kab. Mamasa',
    'Kab. Polewali Mandar' : 'Kab. Polewali Mandar',
    'Kab. Selayar' : 'Kab. Kepulauan Selayar',
    'Kab. Bulu Kumba' : 'Kab. Bulukumba',
    'Kab. Jemeponto' : 'Kab. Jeneponto',
    'Kab. Gua' : 'Kab. Gowa',
    'Kab. Patanjene' : 'Kab. Pangkajene Kepulauan',
    'Kab. SID Ramppang' : 'Kab. Sidenreng Rappang',
    'Kab. Tana Toraja' : 'Kab. Tana Toraja',
    'Kodya Ujungpandang' : 'Kota Makassar',
    'Kodya Pare-pare' : 'Kota Parepare',
    'Kab. Tana Toraja Utara' : 'Kab. Toraja Utara',

    'Kab. Luwuk/Banggai' : 'Kab. Banggai',
    'Kab. Buol Toli-toli' : 'Kab. Buol',
    'Kab. Banggai Kepulauan' : 'Kab. Banggai Kepulauan',
    'Kab. Morowali' : 'Kab. Morowali',
    'Kab. Toli Toli' : 'Kab. Tolitoli',
    'Kodya Palu' : 'Kota Palu',
    'Kab. Parigi Moutong' : 'Kab. Parigi Moutong',
    'Kab. Tojo Una-Una' : 'Kab. Tojo Una-Una',
    'Kab. Banggai Laut' : 'Kab. Banggai Laut',
    'Kab. Morowali Utara' : 'Kab. Morowali Utara',
    'Kodya Kendari' : 'Kota Kendari',

    'Kabupaten Bombana' : 'Kab. Bombana',
    'Kabupaten Buton' : 'Kab. Buton',
    'Kabupaten Buton Selatan' : 'Kab. Buton Selatan',
    'Kabupaten Buton Tengah' : 'Kab. Buton Tengah',
    'Kabupaten Buton Utara' : 'Kab. Buton Utara',
    'Kabupaten Kolaka' : 'Kab. Kolaka',
    'Kabupaten Kolaka Timur' : 'Kab. Kolaka Timur',
    'Kabupaten Kolaka Utara' : 'Kab. Kolaka Utara',
    'Kabupaten Konawe' : 'Kab. Konawe',
    'Kabupaten Konawe Kepulauan' : 'Kab. Konawe Kepulauan',
    'Kabupaten Konawe Selatan' : 'Kab. Konawe Selatan',
    'Kabupaten Konawe Utara' : 'Kab. Konawe Utara',
    'Kabupaten Muna' : 'Kab. Muna',
    'Kabupaten Muna Barat' : 'Kab. Muna Barat',
    'Kabupaten Wakatobi' : 'Kab. Wakatobi',
    'Kota Bau-Bau' : 'Kota Baubau',

    'Kab. Bolaang Mon' : 'Kab. Bolaang Mongondow',
    'Kodya Gorontalo' : 'Kota Gorontalo',
    'Kodya Manado' : 'Kota Manado',
    'Kodya Bitung' : 'Kota Bitung',
    'Kab. Kepulauan Sangihe' : 'Kab. Kep. Sangihe',
    'Kab. Minahasa Selatan' : 'Kab. Minahasa Selatan',
    'Kab. Bolaang Mongondow Utara' : 'Kab. Bolaang Mongondow Utara',
    'Kab. Siau Tagulandang Biaro' : 'Kab. Kepulauan Siau Tagulandang Biaro',
    'Kab. Bolaang Mongondow Timur' : 'Kab. Bolaang Mongondow Timur',
    'Kab. Bolaang Mongondow Selatan' : 'Kab. Bolaang Mongondow Selatan',

    'Kab. Sawah Lunto' : 'Kota Sawah Lunto',
    'Kab. Limapuluh Kota' : 'Kab. Lima Puluh Koto',
    'Kab. Pasaman' : 'Kab. Pasaman',
    'Kodya Padang' : 'Kota Padang',
    'Kodya Solok' : 'Kota Solok',
    'Kodya Sawah Lunto' : 'Kota Sawah Lunto',
    'Kodya Padang Panjang' : 'Kota Padang Panjang',
    'Kodya Bukittinggi' : 'Kota Bukittinggi',
    'Kodya Payakumbuh' : 'Kota Payakumbuh',
    'Kab. Kep. Mentawai' : 'Kab. Kepulauan Mentawai',
    'Kab. Solok Selatan' : 'Kab. Solok Selatan',
    'Kab. Dharmas Raya' : 'Kab. Dharmasraya',
    'Kab. Pasaman Barat' : 'Kab. Pasaman Barat',
    'Kota Pariaman' : 'Kota Pariaman',
    'Kab. Sijunjung' : 'Kab. Sijunjung',
    'Kab. Kubu Raya' : 'Kab. Kuburaya',

    'Kab. Ogan Komering Ulu' : 'Kab. Ogan Komering Ulu',
    'Kab. Ogan Komering Ilir' : 'Kab. Ogan Komering Ilir',
    'Kab. Muara Enim/Liot' : 'Kab. Muara Enim',
    'Kab. Lamat' : 'Kab. Lahat',
    'Kab. Musi Rawas' : 'Kab. Musi Rawas',
    'Kab. Musi Banyu Asin' : 'Kab. Musi Banyuasin',
    'Kodya Palembang' : 'Kota Palembang',
    'Kab. Banyuasin' : 'Kab. Banyuasin',
    'Kab. Ogan Komering Ulu Timur' : 'Kab. Ogan Komering Ulu Timur',
    'Kab. Ogan Komering Ulu Sel.' : 'Kab. Ogan Komering Ulu Selatan',
    'Kota Prabumulih' : 'Kota Prabumulih',
    'Penukal Abab Lematang Ilir' : 'Kab. Penukal Abab Lematang Ilir',
    'kab. Musi Rawas Utara' : 'Kab. Musi Rawas Utara',
    'Kab. Labuhan Batu' : 'Kab. Labuhan Batu',
    'Kodya Sibulga' : 'Kota Sibolga',
    'Kodya Tanjung Balai' : 'Kota Tanjung Balai',
    'Kodya P. Siantar' : 'Kota Pematangsiantar',
    'Kodya Tebingtinggi' : 'Kota Tebing Tinggi',
    'Kodya Medan' : 'Kota Medan',
    'Kodya Binjai' : 'Kota Binjai',
    'Kab. Mandailing Natal' : 'Kab. Mandailing Natal',
    'Kab. Toba Samosir' : 'Kab. Toba',
    'Kab. Nias Selatan' : 'Kab. Nias Selatan',
    'Kab. Pak pak Bharat' : 'Kab. Pakpak Bharat',
    'Kab. Humbang Hasundutan' : 'Kab. Humbang Hasudutan',
    'Kab. Samosir' : 'Kab. Samosir',
    'Kab. Serdang Bedagai' : 'Kab. Serdang Bedagai',
    'Kab. Batu Bara' : 'Kab. Batubara',
    'Kab. Padang Lawas Utara' : 'Kab. Padang Lawas utara',
    'Kab. Padang Lawas' : 'Kab. Padang Lawas',
    'Kab. Labuhanbatu Utara' : 'Kab. Labuhan Batu Utara',
    'Kab. Labuhanbatu Selatan' : 'Kab. Labuhan Batu Selatan',
    'Kab. Nias Barat' : 'Kab. Nias Barat',
    'Kota Padang Sidempuan' : 'Kota Padang Sidimpuan',
    'Kota Gunung Sitoli' : 'Kota Gunungsitoli',
    'Kab. Nias Utara' : 'Kab. Nias Utara',

}
wilayah_reference = {
"D.I. Yogyakarta": ["Kab. Kulonprogo", "Kab. Bantul", "Kab. Gunungkidul", "Kab. Sleman", "Kodya Yogyakarta"],
"Bali": ["Kab. Jembrana", "Kab. Tabanan", "Kab. Badung", "Kab. Gianjar", "Kab. Klungkung", "Kab. Bangli", "Kab. Karangasem", "Kab. Buleleng", "Kodya Denpasar"],
"Bangka Belitung": ["Kab. Bangka", "Kab. Belitung", "Kab. Bangka Tengah", "Kab. Bangka Barat", "Kab. Bangka Selatan", "Kab. Belitung Timur", "Kota Pangkalpinang"],
"Banten": ["Kab. Serang", "Kab. Pandeglang", "Kab. Lebak", "Kab. Tangerang", "Kodya Cilegon", "Kodya Tangerang", "Kota Serang", "Kota Tangerang Selatan"],
"Bengkulu": ["Kab. Bengkulu Selatan", "Kab. Rejanglebong", "Kab. Bengkulu Utara", "Kodya Bengkulu", "Kab. Muko-muko", "Kab. Kepahiang", "Kab. Lebong", "Kab. Kaur", "Kab. Seluma", "Kab. Bengkulu Tengah"],
"D.I. Aceh": ["Kab. Aceh Selatan", "Kab. Aceh Tenggara", "Kab. Aceh Timur", "Kab. Aceh Tengah", "Kab. Aceh Barat", "Kab. Aceh Besar", "Kab. Piedi", "Kab. Aceh Utara", "Kodya Banda Aceh", "Kodya Sabang", "Kab. Bireuen", "Kab. Simeuleu", "Kab. Singkil", "Kab. Langsa", "Kab. Aceh Barat Daya", "Kab. Gayo Lues", "Kab. Aceh Jaya", "Kab. Nagan Raya", "Kab. Aceh Tamiang", "Kotif. Aceh Timur", "Kotif. Lhok Seumawe", "Kab. Bener Meriah", "Kab. Pidie Jaya", "Kota Subulussalam"],
"D.K.I Jakarta": ["Jakarta Selatan", "Jakarta Timur", "Jakarta Pusat", "Jakarta Barat", "Jakarta Utara", "Kab. Kepulauan Seribu"],
"Gorontalo": ["Kab. Boalemo", "Kab. Gorontalo", "Kodya Gorontalo", "Kab. Pohuwato", "Kab. Bone Bolango", "Kab. Gorontalo Utara"],
"Jambi": ["Kab. Kerinci", "Kab. Sarulangun", "Kab. Batanghari", "Kab. Tanjung Jabung Timur", "Kab. Muaro Jambi", "Kodya Jambi", "Kab. Bungo", "Kab. Merangin", "Kab. Tebo", "Kab. Tanjung Jabung Barat", "Kota Sungai Penuh"],
"Jawa Barat": ["Kab. Bogor", "Kab. Sukabumi", "Kab. Cianjur", "Kab. Bandung", "Kab. Garut", "Kab. Tasikmalaya", "Kab. Ciamis", "Kab. Kuningan", "Kab. Cirebon", "Kab. Majalengka", "Kab. Sumedang", "Kab. Indramayu", "Kab. Subang", "Kab. Purwakarta", "Kab. Karawang", "Kab. Bekasi", "Kodya Bogor", "Kodya Sukabumi", "Kodya Bandung", "Kodya Cirebon", "Kodya Depok", "Kota Banjar", "Kab. Bandung Barat", "Kota Bekasi", "Kota Cimahi", "Kota Tasikmalaya", "Kab. Pangandaran"],
"Jawa Tengah": ["Kab. Cilacap", "Kab. Banyumas", "Kab. Purbalingga", "Kab. Banjarnegara", "Kab. Kebumen", "Kab. Purworejo", "Kab. Wonosobo", "Kab. Magelang", "Kab. Boyolali", "Kab. Klaten", "Kab. Sukoharjo", "Kab. Wonogiri", "Kab. Karanganyar", "Kab. Sragen", "Kab. Grobogan", "Kab. Blora", "Kab. Rembang", "Kab. Pati", "Kab. Kudus", "Kab. Jepara", "Kab. Demak", "Kab. Semarang", "Kab. Temanggung", "Kab. Kendal", "Kab. Batang", "Kab. Pekalongan", "Kab. Pemalang", "Kab. Tegal", "Kab. Brebes", "Kodya Magelang", "Kodya Surakarta", "Kodya Salatiga", "Kodya Semarang", "Kodya Pekalongan", "Kodya Tegal"],
"Jawa Timur": ["Kab. Pacitan", "Kab. Ponorogo", "Kab. Trenggalek", "Kab. Tulungagung", "Kab. Blitar", "Kab. Kediri", "Kab. Malang", "Kab. Lumajang", "Kab. Jember", "Kab. Banyuwangi", "Kab. Bondowoso", "Kab. Situbondo", "Kab. Probolinggo", "Kab. Pasuruan","Kab. Sidoarjo", "Kab. Mojokerto", "Kab. Jombang", "Kab. Madiun", "Kab. Nganjuk", "Kab. Magetan", "Kab. Ngawi", "Kab. Bojonegoro", "Kab. Tuban", "Kab. Lamongan", "Kab. Gresik", "Kab. Bangkalan", "Kab. Sampang", "Kab. Pamekasan", "Kab. Sumenep", "Kodya Kediri", "Kodya Blitar", "Kodya Malang", "Kodya Probolinggo", "Kodya Pasuruan", "Kodya Mojokerto", "Kodya Madiun", "Kodya Surabaya", "Kab. Magetan", "Kab. Bangkalan", "Kota Batu"],
"Kalimantan Barat" : ["Kab. Sambas", "Kab. Pontianak", "Kab. Sanggau", "Kab. Ketapang", "Kab. Sintang", "Kab. Kapuas Hulu", "Kodya Pontianak", "Kab. Bengkayang", "Kab. Landak", "Kab. Sekadau", "Kab. Melawi", "Kab. Kayong Utara", "Kab. Kubu Raya", "Kota Singkawang", "Kab. Mempawah"],
"Kalimantan Selatan" : ["Kab. Taman Laut", "Kab. Kota Baru", "Kab. Banjar", "Kab. Barito Kuala", "Kab. Tapin/Tapian", "Kab. Hulu Sei Selatan", "Kab. Hulu Sei Tengah", "Kab. Hulu Sei Utara", "Kab. Tabalong", "Kodya Banjarmasin", "Kab. Balangan", "Kab. Tanah Bumbu", "Kota Banjarbaru"],
"Kalimantan Tengah" :  ["Kab. Kota Waringin Barat", "Kab. Kota Waringin Timur", "Kab. Katingan", "Kab. Kapuas", "Kab. Barito Selatan", "Kab. Barito Timur", "Kab. Barito Utara", "Kab. Gunung Mas", "Kab. Murung Raya", "Kab. Seruyan", "Kodya Palangkaraya", "Kab. Katingan", "Kab. Seruyan", "Kab. Sukamara", "Kab. Lamandau", "Kab. Gunung Mas", "Kab. Pulau Pisau", "Kab. Murung Raya", "Kab. Barito Timur", "Kab. Kutai Timur"],
"Kalimantan Timur" :   ["Kab. Pasir", "Kab. Kutai", "Kab. Berau", "Kab. Bulungan", "Kodya Balikpapan", "Kodya Samarinda", "Kab. Kutai Barat", "Kab. Malinau", "Kab. Nunukan", "Kab. Penajam Paser Utr", "Kodya Bontang", "Kodya Tarakan", "Kab. Kutai Kartanegara", "Kab. Kutai Barat", "Kab. Kutai Timur", "Kab. Tana Tidung", "Kab. Mahakam Ulu"],
"Kalimantan Utara" :  ["Kab. Bulungan", "Kab. Malinau", "Kab. Nunukan", "Kab. Tana Tidung", "Kota Tarakan"],
"Kepulauan Riau" :  ["Kab. bangka", "Kab. Belitung", "Kodya Pangkal Pinang", "Kab. Bangka Tengah", "Kab. Bangka Barat", "Kab. Bangka Selatan", "Kab. Belitung Timur"],
"Lampung" :  ["Kab. Lampung Selatan", "Kab. Lampung Tengah", "Kab. Lampung Utara", "Kodya Tanjung Karang", "Kab. Lampung Timur", "Kab. Lampung Barat", "Kab. Tulang Bawang", "Kab. Way Kanan", "Kodya Bandar Lampung", "Kodya Metro", "Kab. Pesawaran", "Kab. Pringsewu", "Kab. Mesuji", "Kab. Tulang Bawang Barat", "Kab. Pesisir Barat", "Kab. Tanggamus"],
"Luar Negeri" : ["Timor Leste", "Malaysia", "Lainnya"],
"Maluku" : ["Kab. Maluku Tenggara", "Kab. Maluku Tengah", "Kab. Halmahera Tengah", "Kab. Maluku Utara", "Kodya Ambon", "Kab. Maluku Teng Barat", "Kab. Buru", "Kab. Seram Bagian Barat", "Kab. Seram Bagian Timur", "Kab. Kepulauan Aru", "Kab. Maluku Barat Daya", "Kab. Buru Selatan", "Kota Tual", "Kab.Kepulauan Tanimbar"],
"Maluku Utara" : ["Kab. Maluku Utara", "Kab. Pulau Sula", "Kab. Halmahera Tengah", "Kab. Halmahera Selatan", "Kab. Halmahera Utara", "Kab. Halmahera Timur", "Kota Ternate", "Kota Tidore Kepulauan", "Kab. Halmahera Barat", "Kab. Kepulauan Morotai", "Pulau Taliabu"],
"Nusa Tenggara Barat" :  ["Kab. Lombok Barat", "Kab. Lombok Tengah", "Kab. Lombok Timur", "Kab. Sumbawa", "Kab. Dompu", "Kab. Bima", "Kab. Mataram", "Kab. Sumbawa Barat", "Kab. Lombok Utara", "Kota Mataram", "Kota Bima"],
"Nusa Tenggara Timur" :  ["Kab. Sumba Barat", "Kab. Sumba Timur", "Kab. Kupang", "Kab. Timor Tengah Selatan", "Kab. Timor Tengah Utara", "Kab. Belu", "Kab. Alor", "Kab. Flores Timur", "Kab. Sikka", "Kab. Ende", "Kab. Ngade", "Kab. Manggarai", "Kab. Lembata", "Kodya Kupang", "Kab. Rote-Ndao", "Kab. Manggarai Barat", "Kab. Nagekeo", "Kab. Sumba Tengah", "Kab. Sumba Barat Daya", "Kab. Manggarai Timur", "Kab. Sabu Raijua", "Kab. Malaka"],
"Papua Barat": [
    "Kab. Fak Fak", "Kab. Manokwari", "Kab. Sorong", "Kota Sorong", "Kab. Kaimana", 
    "Kab. Teluk Wondama", "Kab. Teluk Bintuni", "Kab. Sorong Selatan", "Kab. Kep. Raja Ampat", 
    "Kab. Tambrauw", "Kab. Maybrat", "Kab. Pegunungan Arfak", "Kab. Manokwari Selatan"
],
"Papua Timur": [
    "Kab. Jayapura", "Kab. Jayawijaya", "Kab. Merauke", "Kab. Puncak Jaya", "Kodya Jayapura"
],
"Prov. Kepulauan Riau": [
    "Kab. Bintan", "Kab. Karimun", "Kab. Natuna", "Kab. Lingga", "Kab. Kep. Anambas", 
    "Kota Batam", "Kota Tanjung Pinang"
],
"Prov. Papua": [
    "Kab. Biak Numfor", "Kab. Mimika", "Kab. Nabire", "Kab. Panial", "Kab. Yapen Waropen", 
    "Kab. Jayapura", "Kab. Yapen Waropen", "Kab. Merauke", "Kab. Jayawijaya", "Kab. Paniai", 
    "Kab. Puncak Jaya", "Kab. Boven Digoel", "Kab. Mappi", "Kab. Asmat", "Kab. Yahukimo", 
    "Kab. Pegunungan Bintang", "Kab. Tolikara", "Kab. Sarmi", "Kab. Keerom", "Kab. Waropen", 
    "Kab. Supiori", "Kab. Memberamo Raya", "Kab. Nduga Tengah", "Kab. Lanny Jaya", 
    "Kab. Mamberamo Tengah", "Kab. Yalimo", "Kab. Puncak", "Kab. Dogiyai", "Kab. Deiyai", 
    "Kab. Intan Jaya", "Kota Jayapura"
],
"Riau": [
    "Kab. Indragiri Ulu", "Kab. Indragiri Hilir", "Kab. Kepulauan Riau", "Kab. Kampar", 
    "Kab. Bengkalis", "Kodya Pekanbaru", "Kodya Batam", "Kab. Kuantan Singingi", "Kab. Pelalawan", 
    "Kab. Siak", "Kab. Rokan Hilir", "Kab. Rokan Hulu", "Kab. Karimun", "Kab. Kepulauan Riau", 
    "Kab. Kota Batam", "Kab. Natuna", "Kab. Tanjung Pinang", "Kodya Dumai", "Kodya Tanjung Pinang", 
    "Kab. Kep. Meranti"
],
"Sulawesi Barat": [
    "Kab. Mamuju", "Kab. Mamuju Utara", "Kab. Polewali Mandar", "Kab. Mamasa", "Kab. Majene", 
    "Kab. Pasangkayu", "Kab. Mamuju Tengah"
],
"Sulawesi Selatan": [
    "Kab. Selayar", "Kab. Bulu Kumba", "Kab. Bantaeng", "Kab. Jeneponto", "Kab. Takalar", 
    "Kab. Gowa", "Kab. Sinjai", "Kab. Bone", "Kab. Maros", "Kab. Pangkajene", "Kab. Barru", 
    "Kab. Soppeng", "Kab. Wajo", "Kab. Sidrap", "Kab. Pinrang", "Kab. Enrekang", "Kab. Luwu", 
    "Kab. Tana Toraja", "Kab. Olewali Mamasa", "Kab. Majene", "Kab. Mamuju", "Kodya Ujungpandang", 
    "Kodya Pare-pare", "Kab. Luwu Utara", "Kota Watampone", "Kab. Tana Toraja Utara", 
    "Kab. Luwu Timur", "Kota Palopo"
],
"Sulawesi Tengah": [
    "Kab. Luwuk/Banggai", "Kab. Poso", "Kab. Donggala", "Kab. Buol", "Kab. Toli-Toli", 
    "Kab. Banggai Kepulauan", "Kab. Morowali", "Kab. Toli Toli", "Kodya Palu", "Kab. Banggai", 
    "Kab. Parigi Moutong", "Kab. Tojo Una-Una", "Kab. Sigi", "Kab. Banggai Laut", "Kab. Morowali Utara"
],
"Sulawesi Tenggara": [
    "Kabupaten Bombana", "Kabupaten Buton", "Kabupaten Buton Selatan", "Kabupaten Buton Tengah", 
    "Kabupaten Buton Utara", "Kabupaten Kolaka", "Kabupaten Kolaka Timur", "Kabupaten Kolaka Utara", 
    "Kabupaten Konawe", "Kabupaten Konawe Kepulauan", "Kabupaten Konawe Selatan", "Kabupaten Konawe Utara", 
    "Kabupaten Muna", "Kabupaten Muna Barat", "Kabupaten Wakatobi", "Kota Bau-Bau", "Kota Kendari"
],
"Sulawesi Utara": [
    "Kab. Gorontalo", "Kab. Bolaang Mongondow", "Kab. Minahasa", "Kab. Kepulauan Talaud", "Kodya Gorontalo", 
    "Kodya Manado", "Kab. Boalemo", "Kodya Bitung", "Kab. Kepulauan Sangihe", "Kab. Minahasa Selatan", 
    "Kab. Minahasa Utara", "Kab. Bolaang Mongondow Utara", "Kab. Siau Tagulandang Biaro", "Kab. Minahasa Tenggara", 
    "Kab. Bolaang Mongondow Timur", "Kab. Bolaang Mongondow Selatan", "Kota Tomohon", "Kota Kotamobagu"
],
"Sumatra Barat": [
    "Kab. Pesisir Selatan", "Kab. Solok", "Kab. Sawah Lunto", "Kab. Tanah Datar", "Kab. Padang Pariaman", 
    "Kab. Agam", "Kab. Limapuluh Kota", "Kab. Pasaman", "Kodya Padang", "Kodya Solok", "Kodya Sawah Lunto", 
    "Kodya Padang Panjang", "Kodya Bukittinggi", "Kodya Payakumbuh", "Kab. Kep. Mentawai", "Kab. Solok Selatan", 
    "Kab. Dharmas Raya", "Kab. Pasaman Barat", "Kota Pariaman", "Kab. Sijunjung"
],
"Sumatra Selatan": [
    "Kab. Ogan Komering Ulu", "Kab. Ogan Komering Ilir", "Kab. Muara Enim", "Kab. Lahat", "Kab. Musi Rawas", 
    "Kab. Musi Banyu Asin", "Kab. Bangka", "Kab. Belitung", "Kodya Palembang", "Kodya Pangkal Pinang", 
    "Kab. Banyuasin", "Kab. Ogan Komering Ulu Timur", "Kab. Ogan Komering Ulu Sel.", "Kab. Ogan Ilir", 
    "Kab. Empat Lawang", "Kota Prabumulih", "Kota Lubuk Linggau", "Kota Pagar Alam", 
    "Kab. Penukal Abab Lematang Ilir", "Kab. Musi Rawas Utara"
],
"Sumatra Utara": [
    "Kab. Nias", "Kab. Tapanuli Selatan", "Kab. Tapanuli Tengah", "Kab. Tapanuli Utara", "Kab. Labuhan Batu", 
    "Kab. Asahan", "Kab. Simalungun", "Kab. Dairi", "Kab. Karo", "Kab. Deli Serdang", "Kab. Langkat", 
    "Kodya Sibolga", "Kodya Tanjung Balai", "Kodya P. Siantar", "Kodya Tebingtinggi", "Kodya Medan", 
    "Kodya Binjai", "Kab. Mandailing Natal", "Kab. Toba Samosir", "Kota Rantau Prapat", "Kab. Nias Selatan", 
    "Kab. Pakpak Bharat", "Kab. Humbang Hasundutan", "Kab. Samosir", "Kab. Serdang Bedagai", "Kab. Batu Bara", 
    "Kab. Padang Lawas Utara", "Kab. Padang Lawas", "Kab. Labuhanbatu Utara", "Kab. Labuhanbatu Selatan", 
    "Kab. Nias Barat", "Kota Padang Sidempuan", "Kota Gunung Sitoli", "Kab. Nias Utara"
]

}

def roman_to_int(roman):
    """
    Mengonversi angka Romawi menjadi angka desimal (integer).
    """
    roman = roman.upper()  # Pastikan huruf besar
    
    roman_numerals = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 
        'D': 500, 'M': 1000
    }

    roman_pattern = r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"

    if not re.match(roman_pattern, roman):
        return None  # Jika tidak valid, return None

    total = 0
    prev_value = 0

    for char in reversed(roman):  # Iterasi dari belakang ke depan
        value = roman_numerals[char]
        if value < prev_value:
            total -= value  # Contoh: IV = 4, IX = 9
        else:
            total += value
        prev_value = value
    
    return total

def normalize_name(name):
    name = name.upper().strip()  # Ubah ke huruf besar dan hapus spasi berlebih
    # Khusus untuk mengubah "SMA N" atau "SMA NEGERI" menjadi "SMAN"
    name = re.sub(r'\b(SMA|SMK)\s+N\b', r'\1N', name)
    name = re.sub(r'\b(SMA|SMK)\s+NEGERI\b', r'\1N', name)
    name = name.replace(",", "").strip()  # Menghilangkan kata "KOTA"
    # Menambahkan spasi antara angka dan kata
    name = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', name)  # Menambahkan spasi antara angka dan huruf
    name = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', name)  # Menambahkan spasi antara huruf dan angka
    name = name.replace("KOTA", "").strip()  # Menghilangkan kata "KOTA"
    name = re.sub(r'\s+', ' ', name)
    # Menghilangkan titik di dalam singkatan seperti PEM., dll.
    name = re.sub(r"\s*\.\s*", " ", name)  # Menghapus titik di antara kata yang memiliki spasi
    # Hapus karakter titik (.) yang tidak perlu
    name = re.sub(r"(?<=\w)\.(?=\w)", ". ", name)  # Contoh: ST.LOUIS → ST. LOUIS
    # Menghapus hanya tanda kurung, tanpa menghapus isi dalamnya
    name = re.sub(r"\((.*?)\)", r"\1", name)  # Hanya menghapus tanda kurung, mempertahankan teks di dalamnya
    # Normalisasi angka (hapus angka yang dimulai dengan 0)
    name = re.sub(r'\b0(\d+)\b', r'\1', name)  # Mengubah "02" menjadi "2", "01" menjadi "1"
    # Normalisasi angka Romawi ke angka biasa
    roman_match = re.findall(r'\b[MCDXLIV]+(?=\s|\b)', name)  # Temukan angka Romawi yang valid
    for roman in roman_match:
        num = roman_to_int(roman)
        if num is not None:  # Jika angka Romawi valid, ganti dengan angka desimal
            name = name.replace(roman, str(num))
    # Terapkan normalisasi berdasarkan NORMALIZATION_MAP
    for key, value in NORMALIZATION_MAP.items():
        name = re.sub(rf'\b{re.escape(key)}\b', value, name, flags=re.IGNORECASE)  
        name = re.sub(rf'\b{re.escape(key)}\s*\.\s*\b', value, name, flags=re.IGNORECASE)
    name = name.upper().strip()  # Ubah ke huruf besar dan hapus spasi berlebih

    name = name.replace("SMA KRISTEN", "SMAS").replace("SMAK", "SMAS").replace("SMA K ", "SMAS ").replace("SMA KR", "SMAS ").replace("SMA SWASTA KATOLIK", "SMAS").replace("SMA SWASTA", "SMAS").replace("SMU KRISTEN", "SMAS").replace("SMA K.", "SMAS").replace("SMAS KRISTEN", "SMAS").replace("SMA KATHOLIK", "SMAS").replace("SMA KATOLIK", "SMAS").replace("SMA KHATOLIK", "SMAS").replace("SMA KANISIUS", "SMAS").replace("SMAS KATHOLIK", "SMAS").replace("SMAS KATOLIK", "SMAS").replace("SMAS KHATOLIK", "SMAS").replace("SMA S KATOLIK", "SMAS").replace("SMK KRISTEN", "SMKS KRISTEN").replace("SMK KATOLIK", "SMKS KATOLIK")   # Mengganti SMA K dan SMAS K menjadi SMAS
    # Tangani variasi nama sebelum regex berjalan
    name = re.sub(r"\bPL\s*ST\.?\s*", "PANGUDI LUHUR SANTO ", name)  # Tambahkan spasi otomatis
    name = re.sub(r"\bPL\.\s*", "PANGUDI LUHUR ", name)
    # Menambahkan aturan untuk mengganti "ST." menjadi "SANTO"
    name = re.sub(r"\bST\.\s*", "SANTO ", name)  # Mengganti "ST." atau "ST" dengan "SANTO"


    return name.strip()  # Pastikan tidak ada spasi berlebih setelah normalisasi




# Adjust normalization of province names as well
def normalize_province(province):
    province_str = str(province)  # Convert province to string explicitly
    normalized = PROVINCE_NORMALIZATION_MAP.get(province_str, province_str)
    return normalized.upper().strip()

def extract_number(text):
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else None

def get_word_after_number(text):
    words = text.split()
    for i, word in enumerate(words):
        if word.isdigit():
            return words[i + 1] if i + 1 < len(words) else None
    return None


def check_school_type(name):
    """Mengecek jenis sekolah berdasarkan kata kunci dalam nama"""
    if any(sub in name for sub in ["SMAN", "SMA", "SMAS", "SMAK"]):
        return "SMA"
    elif any(sub in name for sub in ["SMKN", "SMK", "SMKS"]):
        return "SMK"
    # Jika tidak ada jenjang yang cocok, return None
    return None
def get_school_status(school_name):
    """
    Fungsi untuk mengidentifikasi status sekolah (negeri/swasta) berdasarkan nama sekolah.
    Misalnya, jika nama sekolah mengandung 'NEGERI' atau 'SWASTA', maka akan diidentifikasi sesuai dengan status tersebut.
    """
    school_name = school_name.upper()
    
    # Cek status berdasarkan kata yang ada di nama sekolah
    if 'NEGERI' in school_name or 'N' in school_name:  # Bisa diperluas sesuai pola lain
        return 'Negeri'
    elif 'SWASTA' in school_name or 'S' in school_name:  # Menambahkan pemeriksaan jika ada 'SWASTA'
        return 'Swasta'
    else:
        # Jika tidak ada keterangan jelas, misalnya 'SMA', 'SMK', dan tidak memiliki kata status
        return 'Tidak Diketahui'


def filter_candidates_by_type(target_name, candidates, target_type):
    if target_type:
        return [c for c in candidates if check_school_type(c) == target_type]
    return candidates


def get_best_match(name, candidates, threshold=82, min_common_words=3):
    """Menentukan kandidat referensi terbaik berdasarkan kecocokan kata."""
    # Pengecekan nama 'ANOMALI' terlebih dahulu
    if name.strip().upper() == 'UNKNOWN':  # Pastikan format standar dan hilangkan spasi ekstra
        return None, 0
    
    
    if not candidates:
        return None, 0
        # Pengecekan jika name == match (DILAKUKAN SEBELUM TOKEN_SET_RATIO)
    for match in candidates:
        if name == match:
            return match, 100  # Jika cocok, langsung return dengan skor 100

    matches = process.extract(name, candidates, scorer=fuzz.token_set_ratio, limit=len(candidates))  
    valid_matches = [(m, s) for m, s in matches if s >= threshold]
    # Cek jika ada valid matches dengan skor 100
    for match, score in valid_matches:
        if score == 100:
            return match, score  # Langsung return jika sudah ada skor 100

    
        # Jika tidak ada kecocokan yang valid dengan token_set_ratio, lanjutkan ke partial_ratio tanpa penyaringan
    if not valid_matches:
        matches = process.extract(name, candidates, scorer=fuzz.partial_ratio, limit=len(candidates))
        # Menyaring hasil dengan threshold 82 untuk partial_ratio
        valid_matches = [(m, s) for m, s in matches if s >= 82]
        # Langsung ambil hasil terbaik dari pencocokan partial_ratio yang memenuhi threshold 82
        if valid_matches:
            best_match = max(valid_matches, key=lambda x: x[1])  # Mengambil yang skor terbaik dari hasil partial_ratio
            return best_match  # Mengembalikan hasil terbaik langsung tanpa penyaringan lebih lanjut     


    if not valid_matches:
        return None, 0
        
    best_match = None
    best_score = 0
    max_common_count = 0
    
    target_number = extract_number(name)
    target_after_numbers = get_word_after_number(name)
    name_words = name.split()
    target_type = check_school_type(name)
    target_status = get_school_status(name)  # Menambahkan status sekolah pada target
    
    for match, score in valid_matches:
        match_words = match.split()
        common_words = set(name_words).intersection(set(match_words))
        common_count = len(common_words)
        match_number = extract_number(match)
        match_after_numbers = get_word_after_number(match)
        match_type = check_school_type(match)
        match_status = get_school_status(match)  # Mendapatkan status sekolah dari kandidat

        # 1️⃣ Cek jenis sekolah untuk memastikan kecocokan jenis (SMK/SMA)
        if target_type and match_type and target_type != match_type:
            continue

        # Jika status target tidak sama dengan status match, dan keduanya memiliki status yang jelas
        # Jika target memiliki status "Tidak Diketahui", maka cocokkan dengan semua status
        if target_status != 'Tidak Diketahui' and match_status != 'Tidak Diketahui' and target_status != match_status:
            continue  # Jika status berbeda, lanjutkan ke kandidat berikutnya

    
        # 2️⃣ **Mutlak - Periksa Angka**
        # Jika ada angka pada nama target dan referensi, pastikan angkanya cocok
        if target_number and match_number and target_number != match_number:
            continue  # Jika angkanya tidak cocok, lanjutkan ke kandidat berikutnya

        # Jika salah satu dari target atau match tidak mengandung angka, maka tidak bisa dicocokkan
        if (target_number and not match_number) or (not target_number and match_number):
            continue  # Eliminasikan jika ada perbedaan pada angka
        
    
        # **Fuzzy matching dengan token_sort_ratio untuk menangani urutan kata yang berbeda, hanya jika ada angka**
        if target_number and match_number:  # Cek jika kedua string memiliki angka
            fuzzy_score = fuzz.token_sort_ratio(name, match)
            if fuzzy_score >= 95:  # Penerapan token_sort_ratio hanya jika ada angka dan memenuhi threshold
                return match, fuzzy_score  # Langsung return jika sudah memenuhi threshold

            # Jika fuzzy_score kurang dari threshold, lanjutkan ke partial_ratio
            partial_score = fuzz.partial_ratio(name, match)
            if partial_score >= 90:  # Tentukan threshold yang sesuai untuk partial_ratio
                return match, partial_score  # Langsung return jika sudah memenuhi threshold dengan partial_ratio

            # Jika partial_ratio masih kurang dari threshold, lanjutkan ke set_ratio
            set_score = fuzz.token_set_ratio(name, match)
            if set_score >= 90:  # Tentukan threshold yang sesuai untuk set_ratio
                return match, set_score  # Langsung return jika sudah memenuhi threshold dengan token_set_ratio
            
        # Apply token_set_ratio for matches without numbers
        if not target_number and not match_number:
            refined_score = fuzz.token_set_ratio(name, match)
            if refined_score >= 90:  # If the match score is greater than or equal to 85, accept it
                return match, refined_score

            # Proceed with additional fuzzy matching
            partial_score = fuzz.partial_ratio(name, match)
            if partial_score >= 90:
                return match, partial_score

            fuzzy_score = fuzz.token_sort_ratio(name, match)
            if fuzzy_score >= threshold:
                return match, fuzzy_score               

            # 3️⃣ **Periksa Kata Setelah Angka dengan Fuzzy Matching**
        if target_after_numbers and match_after_numbers:
            # Cek terlebih dahulu dengan fuzzy matching menggunakan fuzz.ratio
            ratio = fuzz.ratio(target_after_numbers, match_after_numbers)
            if ratio < 85:  # Jika kesamaan kata setelah angka kurang dari threshold, lanjutkan ke kandidat berikutnya                         
                continue  # Tidak cocok setelah angka, lewati pencocokan
            
        # Jika nama target memiliki kata lebih banyak daripada referensi, kita hanya mencocokkan kata yang ada di kedua tempat
        if len(name_words) != len(match_words):
            common_count = len(set(name_words).intersection(set(match_words)))
            if common_count >= min_common_words:  # Jika ada cukup banyak kata yang sama
                return match, score

        # 8️⃣ **Memprioritaskan kecocokan tanpa memperhatikan urutan kata**
        # Menyaring kata-kata yang sama dalam kedua nama (tanpa urutan)
        common_words = set(name_words).intersection(set(match_words))
        if len(common_words) >= min_common_words:
            return match, score

        # **Fuzzy matching dengan token_sort_ratio untuk menangani urutan kata yang berbeda**
        fuzzy_score = fuzz.token_sort_ratio(name_words, match_words)
        
        # Jika fuzzy_score memenuhi threshold, kembalikan hasilnya
        if fuzzy_score >= threshold:
            return match_words, fuzzy_score
        
        # Jika tidak memenuhi, cek dengan partial_ratio
        partial_score = fuzz.partial_ratio(name_words, match_words)
        if partial_score >= threshold:
            return match_words, partial_score


        # Simpan kecocokan terbaik berdasarkan jumlah kata yang sama dan skor tertinggi
        if common_count > max_common_count or (common_count == max_common_count and score > best_score):
            best_match = match
            best_score = score
            max_common_count = common_count

        if score > best_score:
            best_match, best_score = match, score
            # After all checks, return the best match found using token_set_ratio if no better match is found
    
    return best_match, best_score



# Adjust normalization of province names as well
def normalize_kabupaten(kabupaten):
    kabupaten_str = str(kabupaten)  # Convert province to string explicitly
    normalized = KABUPATEN_NORMALIZATION_MAP.get(kabupaten_str, kabupaten_str)
    return normalized.upper().strip()

# Function to load JSON files with reference data
def load_json_files(folder_path='./hasil'):
    all_school_data = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
                data = json.load(file)

                for key in data:
                    for school in data[key]:
                        if school['bentuk'] in ['SMA', 'SMK', 'MA', 'MAK', 'PKBM']:
                            normalized_name = normalize_name(school['sekolah'])
                            kabupaten = normalize_kabupaten(school.get('kabupaten_kota', ''))
                            provinsi = normalize_province(school.get('propinsi', ''))

                            # Store normalized_name for quick lookup
                            full_key_kabupaten = f"{normalized_name}, {kabupaten}"
                            full_key_provinsi = f"{normalized_name}, {provinsi}"
                            all_school_data[full_key_kabupaten] = normalized_name
                            all_school_data[full_key_provinsi] = normalized_name

    return all_school_data

def load_rename_references(folder_path='./hasil'):
    rename_references = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
                data = json.load(file)

                for key in data:
                    for school in data[key]:
                        if school['bentuk'] in ['SMA', 'SMK', 'MA', 'MAK', 'PKBM']:
                            normalized_name = normalize_name(school['sekolah'])
                            kabupaten = normalize_kabupaten(school.get('kabupaten_kota', ''))
                            provinsi = normalize_province(school.get('propinsi', ''))

                            # Store the kabupaten and provinsi for the given normalized name
                            full_key = f"{normalized_name}"
                            rename_references[full_key] = {'kabupaten': kabupaten, 'provinsi': provinsi}

    return rename_references


# Load references
reference_names = load_json_files()
# Load reference data for renaming
rename_references = load_rename_references()
# Instantiate Nominatim geolocator
geolocator = ArcGIS()
# Function to load the coordinates cache from file
def load_coordinates_cache(coordinates_cache_file='coordinates_cache.json'):
    if os.path.exists(coordinates_cache_file):
        with open(coordinates_cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Function to update the coordinates cache to the file
def update_coordinates_cache(coordinates_cache, coordinates_cache_file='coordinates_cache.json'):
    with open(coordinates_cache_file, 'w', encoding='utf-8') as f:
        json.dump(coordinates_cache, f, ensure_ascii=False, indent=4)

# Function to get coordinates, using cache first, then geocoding
def get_coordinates(school_name, coordinates_cache):
    if school_name == 'unknown':
        return (None, None)
    # If the school name exists in the cache, return the cached coordinates
    if school_name in coordinates_cache:
        return coordinates_cache[school_name]
    
    # If not in cache, use the geolocator
    try:
        location = geolocator.geocode(school_name + ", Indonesia")
        if location:
            coordinates = (location.latitude, location.longitude)
            coordinates_cache[school_name] = coordinates
            # Update the cache file with the new coordinates
            update_coordinates_cache(coordinates_cache)
            return coordinates
        else:
            return (None, None)
    except Exception as e:
        print(f"Error geocoding {school_name}: {e}")
        return (None, None)
    
# Function to rename kota_sek and prop_sek based on reference data
def rename_kota_prov(df, rename_references):
    # Loop through the rows of the DataFrame
    for index, row in df.iterrows():
        school_name = row['nama_sekolah']
        kabupaten = row['kota_sek']
        provinsi = row['prop_sek']
            # Jika nama sekolah adalah 'anomali', lewati penggantian kota dan provinsi
        if school_name == 'unknown':
            continue
        # Normalize the names (convert to uppercase and strip any extra spaces)
        normalized_name = normalize_name(school_name)
        kabupaten_normalized = normalize_kabupaten(kabupaten)
        provinsi_normalized = normalize_province(provinsi)

        # Case 1: Exact match for nama_sekolah and kabupaten (kota_sek) in reference
        full_key_kabupaten = f"{normalized_name}, {kabupaten_normalized}"
        if full_key_kabupaten in rename_references:
            reference_data = rename_references[full_key_kabupaten]
            # If kabupaten doesn't match, rename it
            if kabupaten_normalized != reference_data['kabupaten']:
                df.at[index, 'kota_sek'] = reference_data['kabupaten']
            # If propinsi doesn't match, rename it
            if provinsi_normalized != reference_data['provinsi']:
                df.at[index, 'prop_sek'] = reference_data['provinsi']

        # Case 2: Exact match for nama_sekolah and provinsi in reference
        full_key_provinsi = f"{normalized_name}, {provinsi_normalized}"
        if full_key_provinsi in rename_references:
            reference_data = rename_references[full_key_provinsi]
            # If prop_sek doesn't match, rename it
            if provinsi_normalized != reference_data['provinsi']:
                df.at[index, 'prop_sek'] = reference_data['provinsi']
            # If kabupaten doesn't match, rename it
            if kabupaten_normalized != reference_data['kabupaten']:
                df.at[index, 'kota_sek'] = reference_data['kabupaten']

        # Case 3: If nama_sekolah matches, but no match for kabupaten or propinsi
        # In this case, check by nama_sekolah only
        if normalized_name in rename_references:
            reference_data = rename_references[normalized_name]
            if kabupaten_normalized != reference_data['kabupaten']:
                df.at[index, 'kota_sek'] = reference_data['kabupaten']
            if provinsi_normalized != reference_data['provinsi']:
                df.at[index, 'prop_sek'] = reference_data['provinsi']

    return df






def clean_data(df):
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Replace empty strings with NaN
    df.replace("", np.nan, inplace=True)  # Replace empty strings with NaN
    
    # Ganti NaN di kolom 'nama_sekolah' dengan 'anomali'
    df['nama_sekolah'] = df['nama_sekolah'].fillna('unknown')
    
    # Make sure all values in 'nama_sekolah' are strings
    df['nama_sekolah'] = df['nama_sekolah'].astype(str)
    
    # Remove unwanted characters such as '-' and ':'
    df['nama_sekolah'] = df['nama_sekolah'].str.replace(r'[-:]', '', regex=True)
    
    # Replace 'SMA', 'SMK', 'SMAN' with 'anomali' in 'nama_sekolah' only if they are alone (not followed by a number or other text)
    df['nama_sekolah'] = df['nama_sekolah'].apply(lambda x: 'unknown' if x in ['SMA', 'SMK', 'SMAN'] else x)


    df["pilihan1"] = df["pilihan1"].apply(lambda x: f"{int(x):02}" if pd.notna(x) else None)
    df["pilihan2"] = df["pilihan2"].apply(lambda x: f"{int(x):02}" if pd.notna(x) else None)

    # Memetakan kode prodi di kolom 'pilihan1' dan 'pilihan2' ke nama prodi
    df["pilihan1"] = df["pilihan1"].map(prodi_reference).fillna("Tidak Memilih")
    df["pilihan2"] = df["pilihan2"].map(prodi_reference).fillna("Tidak Memilih")

    df["terima"] = df["terima"].apply(lambda x: f"{int(x):02}" if pd.notna(x) else None)
    df["terima"] = df["terima"].map(prodi_reference).fillna("Tidak Lolos")

    
    # Isi nilai kosong pada kolom 'nim'
    df["nim"] = df["nim"].fillna("Tidak Registrasi").astype(str)
    # Isi nilai kosong pada kolom 'kelamin'
    df["kelamin"] = df["kelamin"].fillna("Tidak Diketahui").astype(str)


    # Mengisi nilai kosong pada kolom `kota_sek` dengan nilai dari kolom `kab_sek`
    df['kota_sek'] = df['kota_sek'].fillna(df['kab_sek'])
    # Handle missing 'prop_sek' and 'kota_sek' based on the same 'nama_sekolah'
    df['prop_sek'] = df.groupby('nama_sekolah')['prop_sek'].transform(lambda x: x.ffill().bfill())
    df['kota_sek'] = df.groupby('nama_sekolah')['kota_sek'].transform(lambda x: x.ffill().bfill())

    # Mengganti "D.I. Yogyakarta" dengan "Kodya Yogyakarta" pada kolom kota_sek
    df['kota_sek'] = df['kota_sek'].replace("D.I. Yogyakarta", "Kodya Yogyakarta")
    # Fungsi untuk memeriksa apakah kota_sek sesuai dengan prop_sek
    def validate_kota_sek(row):
        prop_sek = row['prop_sek']
        kota_sek = row['kota_sek']
        kab_sek = row['kab_sek']
        
        # Cek apakah prop_sek ada di wilayah_reference
        if prop_sek in wilayah_reference:
            valid_kota = wilayah_reference[prop_sek]
            
            # 1. Cek apakah kota_sek sesuai dengan prop_sek
            if kota_sek in valid_kota:
                return kota_sek
            
            # 2. Jika kota_sek tidak cocok, cek apakah kab_sek cocok dengan prop_sek
            if kab_sek in valid_kota:
                # Ganti kota_sek dengan kab_sek jika kab_sek cocok
                return kab_sek
            
            # 3. Jika keduanya tidak cocok, kita bisa memilih kota pertama yang valid atau memberi nilai "Kota Tidak Dikenal"
            return valid_kota[0]  # atau bisa menggunakan "Invalid Data" atau nilai lain yang sesuai
        
        return kota_sek  # Jika prop_sek tidak ada dalam wilayah_reference

    # Terapkan fungsi validasi pada setiap baris
    df['kota_sek'] = df.apply(validate_kota_sek, axis=1)
    # Normalisasi nama provinsi menggunakan PROVINCE_NORMALIZATION_MAP
    df['kota_sek'] = df['kota_sek'].apply(lambda x: normalize_kabupaten(x) if pd.notna(x) else x)
    df['prop_sek'] = df['prop_sek'].apply(lambda x: normalize_province(x) if pd.notna(x) else x)

    df = df.drop_duplicates(subset=['no_daftar'])
    df['tgl_daftar'] = pd.to_datetime(df['tgl_daftar'], errors='coerce', dayfirst=True)


    return df


def standardize_school_name(name, reference_names, kabupaten, provinsi, threshold=92):
    """
    Standarisasi nama sekolah berdasarkan data referensi dengan logika:
    1️⃣ **Cek kabupaten dulu**
    2️⃣ **Jika tidak ada di kabupaten, cek di provinsi**
    """
    if name == 'UNKNOWN':
        return "UNKNOWN"  # Langsung kembalikan jika nama adalah "ANOMALI"

    name_cleaned = normalize_name(name) or ""
    kabupaten_cleaned = normalize_kabupaten(kabupaten) or ""
    provinsi_cleaned = normalize_province(provinsi) or ""

    # Cek jenis sekolah (SMA, SMK, SMP, dll.)
    school_type = check_school_type(name_cleaned)
    #result_data = []

    # 1️⃣ CARI DI KABUPATEN TERLEBIH DAHULU
    name_with_kabupaten = f"{name_cleaned}, {kabupaten_cleaned}"
    candidates_kabupaten = [
        ref_name for ref_name in reference_names.keys()
        if ref_name.endswith(f", {kabupaten_cleaned}")
    ]

    # Filter kandidat berdasarkan jenis sekolah
    candidates_kabupaten = filter_candidates_by_type(name_cleaned, candidates_kabupaten, school_type)

    if candidates_kabupaten:
        ref_name, score = get_best_match(name_with_kabupaten, candidates_kabupaten, threshold)
        if ref_name and score >= threshold:
            #result_data.append([name, name_cleaned, ref_name, score, reference_names[ref_name]])
            return reference_names[ref_name]

    # 2️⃣ JIKA TIDAK DITEMUKAN DI KABUPATEN, CEK DI PROVINSI
    name_with_provinsi = f"{name_cleaned}, {provinsi_cleaned}"
    candidates_provinsi = [
        ref_name for ref_name in reference_names.keys()
        if ref_name.endswith(f", {provinsi_cleaned}")
    ]

    # Filter kandidat berdasarkan jenis sekolah
    candidates_provinsi = filter_candidates_by_type(name_cleaned, candidates_provinsi, school_type)

    if candidates_provinsi:
        ref_name, score = get_best_match(name_with_provinsi, candidates_provinsi, threshold)
        if ref_name and score >= threshold:
            #result_data.append([name, name_cleaned, ref_name, score, reference_names[ref_name]])
            return reference_names[ref_name]
        
    # Jika tidak ditemukan, return nama yang sudah dinormalisasi
    #result_data.append([name, name_cleaned, "-", "-", name_cleaned]) //untuk testing
    return name_cleaned




def save_results_excel(results, filename="standardized_schools.xlsx"):
    df = pd.DataFrame(results, columns=["Nama Sekolah Original", "Nama Sekolah Normalisasi", "Nama Sekolah Referensi", "Skor Kemiripan", "Hasil Standarisasi"])
    df.to_excel(filename, index=False)

def process_school_data(df, reference_names):
    """ Proses data sekolah dan simpan hasilnya ke Excel """
    all_results = []
    
    for _, row in df.iterrows():
        standardized_name, result_data = standardize_school_name(row['nama_sekolah'], reference_names, row['kota_sek'], row['prop_sek'])
        all_results.extend(result_data)  # Tambahkan semua hasil ke list utama

    save_results_excel(all_results)  # Simpan hasil ke file Excel


# Grouping and standardizing schools
def group_and_standardize(df, reference_names):
    df['nama_sekolah'] = df.apply(
        lambda row: standardize_school_name(row['nama_sekolah'], reference_names, row['kota_sek'], row['prop_sek']),
        axis=1
    )
    return df


def calculate_choice1_count(cleaned_data):
    cleaned_data = cleaned_data[cleaned_data['nama_sekolah'] != 'UNKNOWN']
    df = cleaned_data.copy()
    df = df[df['pilihan1'] != 'Tidak Memilih']
    choice1_count = df.groupby(['prop_sek', 'kota_sek', 'nama_sekolah', 'pilihan1']).size().reset_index(name='jumlah_choice1')
    choice1_count.rename(columns={'pilihan1': 'program_studi'}, inplace=True)
    return choice1_count


def calculate_choice2_count(cleaned_data):
    cleaned_data = cleaned_data[cleaned_data['nama_sekolah'] != 'UNKNOWN']
    df = cleaned_data.copy()
    df = df[df['pilihan2'] != 'Tidak Memilih']
    choice2_count = df.groupby(['prop_sek', 'kota_sek', 'nama_sekolah', 'pilihan2']).size().reset_index(name='jumlah_choice2')
    choice2_count.rename(columns={'pilihan2': 'program_studi'}, inplace=True)
    return choice2_count


def calculate_lulus_seleksi(cleaned_data):
    df = cleaned_data[
        (cleaned_data['terima'] != 'Tidak Lolos') &
        (cleaned_data['nama_sekolah'] != 'UNKNOWN')
    ]
    diterima_per_prodi = df.groupby(['prop_sek', 'kota_sek', 'nama_sekolah', 'terima']).size().reset_index(name='jumlah_terima')
    diterima_per_prodi.rename(columns={'terima': 'program_studi'}, inplace=True)
    return diterima_per_prodi



def calculate_registrasi(cleaned_data):
    df = cleaned_data[
        (cleaned_data['nim'].notna()) &
        (cleaned_data['nim'] != 'Tidak Registrasi') &
        (cleaned_data['nama_sekolah'] != 'UNKNOWN') &
        (cleaned_data['terima'] != 'Tidak Lolos')
    ]
    registrasi_per_prodi = df.groupby(['prop_sek', 'kota_sek', 'nama_sekolah', 'terima']).size().reset_index(name='jumlah_registrasi')
    registrasi_per_prodi.rename(columns={'terima': 'program_studi'}, inplace=True)
    return registrasi_per_prodi

def merge_all_metrics(filtered_df):
    filtered_df = filtered_df[filtered_df['nama_sekolah'] != 'UNKNOWN']
    
    choice1 = calculate_choice1_count(filtered_df)
    choice2 = calculate_choice2_count(filtered_df)
    lulus = calculate_lulus_seleksi(filtered_df)
    registrasi = calculate_registrasi(filtered_df)

     # Ambil informasi lokasi dan tahun
    location_data = filtered_df[['nama_sekolah', 'prop_sek', 'kota_sek', 'longitude', 'latitude', 'tahun']].drop_duplicates()

    # Merge semua metrik berdasarkan propinsi, kota, sekolah, dan program studi
    merged_df = pd.merge(choice1, choice2, how='outer',
                      on=['prop_sek', 'kota_sek', 'nama_sekolah', 'program_studi'])
    merged_df = pd.merge(merged_df, lulus, how='outer',
                      on=['prop_sek', 'kota_sek', 'nama_sekolah', 'program_studi'])
    merged_df = pd.merge(merged_df, registrasi, how='outer',
                      on=['prop_sek', 'kota_sek', 'nama_sekolah', 'program_studi'])

    # Merge dengan lokasi
    merged_df = pd.merge(merged_df, location_data, on=['prop_sek', 'kota_sek', 'nama_sekolah'], how='left')

    # Isi nilai NaN dengan 0
    merged_df.fillna(0, inplace=True)

    return merged_df
def process_filtered_data(filtered_df, jumlah_cluster):
    filtered_df = filtered_df[filtered_df['nama_sekolah'] != 'UNKNOWN']

    # Merge semua data yang sudah dihitung
    merged_data = merge_all_metrics(filtered_df)  
    merged_data = merged_data.drop_duplicates(subset=['nama_sekolah', 'kota_sek', 'prop_sek', 'program_studi'])
    # Hitung skor berdasarkan bobot
    merged_data['skor'] = (
        merged_data['jumlah_choice1'] * 0.3 +  
        merged_data['jumlah_choice2'] * -0.1 +  
        merged_data['jumlah_registrasi'] * 0.3 +  
        merged_data['jumlah_terima'] * 0.2      
    )

    # Normalisasi skor
    scaler = StandardScaler()
    merged_data['skor_normalized'] = scaler.fit_transform(merged_data[['skor']])

    # Clustering berdasarkan provinsi dan kota
    merged_data['Cluster'] = -1
    iteration_results_prodi = []

    for (provinsi, kota, program_studi), group in merged_data.groupby(['prop_sek', 'kota_sek', 'program_studi']):
        clustering_data = group[['skor_normalized']].to_numpy()

        if len(group) < int(jumlah_cluster):
            clusters = np.zeros(len(group), dtype=int)
            centroids = np.array([group['skor_normalized'].mean()] * jumlah_cluster)
        else:
            kmeans = KMeans(n_clusters=jumlah_cluster, init='k-means++', max_iter=100, tol=1e-4, random_state=42)
            kmeans.fit(clustering_data)
            clusters = kmeans.labels_
            centroids = kmeans.cluster_centers_.flatten()

        centroid_labels = generate_labels_for_clusters(jumlah_cluster, centroids)

        merged_data.loc[group.index, 'Cluster'] = clusters
        for i in range(jumlah_cluster):
            distances = np.abs(group['skor_normalized'] - centroids[i])
            merged_data.loc[group.index, f'Centroid_{i}'] = centroids[i]
            merged_data.loc[group.index, f'Jarak_Centroid_{i}'] = distances

        merged_data.loc[group.index, 'Label_Cluster'] = [centroid_labels[cluster] for cluster in clusters]

        iteration_results_prodi.append({
            "program_studi": program_studi,
            "provinsi": provinsi,
            "kota": kota,
            "centroids": centroids,
            "clusters": clusters
        })

    return merged_data, iteration_results_prodi


def hitung_jumlah_cluster_optimal_per_kota_prodi(df, n_cluster_options=[2, 3, 4]):
    hasil = []

    for kota in df['kota_sek'].unique():
        df_kota = df[df['kota_sek'] == kota]

        X = df_kota[['skor_normalized']].values
        jumlah_data = len(X)

        best_score = -1
        best_cluster = None

        for n in n_cluster_options:
            if jumlah_data > n:
                try:
                    model = KMeans(n_clusters=n, random_state=42, n_init='auto')
                    labels = model.fit_predict(X)
                    # Silhouette hanya valid jika hasil cluster > 1 label
                    if len(set(labels)) > 1:
                        score = silhouette_score(X, labels)
                        if score > best_score:
                            best_score = score
                            best_cluster = n
                except:
                    continue

        # Jika tidak ditemukan jumlah cluster optimal secara valid
        if best_cluster:
            hasil.append({
                'kota_sek': kota,
                'jumlah_cluster_optimal': best_cluster,
                'skor_silhouette': round(best_score, 4)
            })
        else:
            # Default: jumlah cluster optimal = jumlah data (jika 2), atau 1
            fallback_cluster = min(jumlah_data, 2)  # maks 2 agar tetap bisa dibagi dua
            hasil.append({
                'kota_sek': kota,
                'jumlah_cluster_optimal': fallback_cluster,
                'skor_silhouette': None
            })

    return pd.DataFrame(hasil)

def normalize_data(df, columns_to_normalize):
    scaler = StandardScaler()
    df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
    return df
def get_cluster_color(label):
    color_map = {
        'Paling Potensial': 'green',
        'Potensial': 'lightgreen',
        'Cukup Potensial': 'yellow',
        'Tidak Potensial': 'red',
        'Sangat Tidak Potensial': 'darkred'
    }
    return color_map.get(label, 'gray')

# Fungsi untuk agregasi data
def aggregate_and_score(cleaned_data):
    # Pastikan data "ANOMALI" tidak dihitung
    cleaned_data = cleaned_data[cleaned_data['nama_sekolah'] != 'UNKNOWN']

    # Aggregating data by province, city, and school
    grouped_data = cleaned_data.groupby(['prop_sek', 'kota_sek', 'nama_sekolah']).agg(
        total_pendaftar=('nama_sekolah', 'count'),
        total_lulus=('terima', lambda x: x[x != 'Tidak Lolos'].count()),
        total_regist=('nim', lambda x: x[x.notna() & (x != 'Tidak Registrasi')].count()),
        total_batal=('batal', 'sum'),
        awal=('tgl_daftar', lambda x: sum(x.dt.month.isin([1, 2, 3, 4])))  # Early registration
    ).reset_index()

    # Simpan versi original untuk merge
    grouped_data_original = grouped_data.copy()

    return grouped_data, grouped_data_original

def categorize_registration_date(date):
    if pd.isna(date):  # Tangani nilai NaT
        return 'Tidak Diketahui'
    elif date.month in [1, 2, 3, 4]:
        return 'Awal'
    elif date.month in [5, 6, 7, 8]:
        return 'Pertengahan'
    elif date.month in [9, 10, 11, 12]:
        return 'Akhir'
    else:
        return 'Lainnya'

# Fungsi untuk menghitung skor berbobot
@st.cache_data(show_spinner="🔢 Menghitung skor berbobot...")
def calculate_weighted_score(data: pd.DataFrame, df_hash: str):
    # Pastikan data "ANOMALI" tidak dihitung
    data = data[data['nama_sekolah'] != 'UNKNOWN']
    grouped_data, grouped_data_original = aggregate_and_score(data)

    # Bobot untuk setiap kriteria
    bobot = {
        "total_regist": 0.3,
        "total_lulus": 0.2,
        "awal": 0.3,  # Bobot waktu pendaftaran awal
        "total_pendaftar": 0.1,
        "total_batal": -0.3  # Negatif karena pengaruh buruk
    }
    # Hitung nilai * bobot berdasarkan data MENTAH (bukan normalisasi)
    grouped_data['regist_weighted'] = grouped_data['total_regist'] * bobot['total_regist']
    grouped_data['lulus_weighted'] = grouped_data['total_lulus'] * bobot['total_lulus']
    grouped_data['awal_weighted'] = grouped_data['awal'] * bobot['awal']
    grouped_data['pendaftar_weighted'] = grouped_data['total_pendaftar'] * bobot['total_pendaftar']
    grouped_data['batal_weighted'] = grouped_data['total_batal'] * bobot['total_batal']

    # Hitung bobot waktu berdasarkan data normalisasi
    grouped_data['bobot_waktu'] = grouped_data['awal'] * bobot['awal']

    # Hitung skor akhir berdasarkan data normalisasi
    grouped_data['skor_akhir'] = (
        grouped_data['total_regist'] * bobot['total_regist'] +
        grouped_data['total_lulus'] * bobot['total_lulus'] +
        grouped_data['bobot_waktu'] +
        grouped_data['total_pendaftar'] * bobot['total_pendaftar'] +
        grouped_data['total_batal'] * bobot['total_batal']
    )

    # Urutkan berdasarkan skor akhir (descending)
    grouped_data_sorted = grouped_data.sort_values(by='skor_akhir', ascending=False)
    
    # Gabungkan data asli untuk ditampilkan
    final_data = pd.merge(
        grouped_data_original,
        grouped_data[['nama_sekolah', 'prop_sek', 'kota_sek', 'bobot_waktu', 'skor_akhir']],
        on=['nama_sekolah', 'prop_sek', 'kota_sek'],
        how='left'
    )

    return final_data, grouped_data

def generate_labels_for_clusters(optimal_clusters, centroids):
    # Label positif dari yang tertinggi
    if optimal_clusters == 2:
        positive_labels = ['Potensial']
    elif optimal_clusters == 3:
        positive_labels = ['Potensial', 'Cukup Potensial']
    else:
        positive_labels = ['Potensial', 'Cukup Potensial', 'Kurang Potensial']
    # Urutkan centroid dari besar ke kecil
    indexed_centroids = list(enumerate(centroids))
    sorted_centroids = sorted(indexed_centroids, key=lambda x: x[1], reverse=True)

    label_mapping = {}
    for rank, (idx, value) in enumerate(sorted_centroids):
        if rank < len(positive_labels):
            label_mapping[idx] = positive_labels[rank]
        else:
            label_mapping[idx] = 'Tidak Potensial'
    
    return label_mapping




def hitung_jumlah_cluster_optimal_provinsi_prodi(df, score_column='total_score_normalized_prov', n_cluster_options=[2, 3, 4]):
    hasil = []

    X = df[[score_column]].values
    jumlah_data = len(X)

    best_score = -1
    best_cluster = None

    for n in n_cluster_options:
        if jumlah_data > n:
            try:
                model = KMeans(n_clusters=n, random_state=42, n_init='auto')
                labels = model.fit_predict(X)
                if len(set(labels)) > 1:
                    score = silhouette_score(X, labels)
                    if score > best_score:
                        best_score = score
                        best_cluster = n
            except:
                continue

    if best_cluster:
        hasil.append({
            'jumlah_cluster_optimal': best_cluster,
            'skor_silhouette': round(best_score, 4)
        })
    else:
        fallback_cluster = min(jumlah_data, 2)
        hasil.append({
            'jumlah_cluster_optimal': fallback_cluster,
            'skor_silhouette': None
        })

    return pd.DataFrame(hasil)

# Fungsi untuk clustering program studi berdasarkan total skor_normalized di provinsi
def cluster_program_study_by_province(data):
    # Group by province and calculate total normalized score for each province
    province_data = data.groupby(['prop_sek', 'program_studi'])['skor'].sum().reset_index(name='total_score')
    return province_data
# Fungsi untuk clustering program studi berdasarkan total skor_normalized di provinsi
def cluster_program_study_by_province1(clustered_data, selected_prodi):
    # Group by province and calculate total normalized score for each province
    province_data = clustered_data.groupby(['prop_sek', 'program_studi'])['skor'].sum().reset_index(name='total_score')
    return province_data
def normalize_total_score_prov_prodi(data):
    # Inisialisasi StandardScaler
    scaler = StandardScaler()

    # Normalisasi skor akhir
    normalized_scores = scaler.fit_transform(data[['total_score']])

    # Menambahkan kolom 'total_score_normalized' ke dalam data
    data['total_score_normalized'] = normalized_scores.flatten()

    return data

def kmeans_cluster_program_province(clustered_data, optimal_clusters):
    result = []

    for program_studi, group in clustered_data.groupby('program_studi'):
        # Normalisasi
        scaler = StandardScaler()
        normalized_scores = scaler.fit_transform(group[['total_score']])
        group['total_score_normalized'] = normalized_scores.flatten()

        # KMeans
        kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', max_iter=100, tol=1e-4, random_state=42)
        kmeans.fit(normalized_scores)

        group['Cluster'] = kmeans.labels_
        centroids = kmeans.cluster_centers_.flatten()

        # Jarak ke centroid
        for i, centroid in enumerate(centroids):
            group[f'Centroid_{i}'] = centroid
            group[f'Jarak_Centroid_{i}'] = np.abs(group['total_score_normalized'] - centroid)

        # Label cluster
        centroid_labels = generate_labels_for_clusters(optimal_clusters, centroids)
        group['Label_Cluster'] = group['Cluster'].map(centroid_labels)

        result.append(group)

    return pd.concat(result, ignore_index=True)

# Fungsi untuk clustering program studi berdasarkan total skor_normalized di kota/kabupaten
def cluster_program_study_by_city(clustered_data):
    # Group by province and city and calculate total normalized score for each city
    city_data = clustered_data.groupby(['prop_sek', 'kota_sek', 'program_studi'])['skor'].sum().reset_index(name='total_score')
    return city_data

def kmeans_cluster_program_city(clustered_data, jumlah_cluster):
    final_data = []

    for (provinsi, program_studi), group in clustered_data.groupby(['prop_sek', 'program_studi']):
        num_cities = len(group)

        if num_cities == 1:
            group['Label_Cluster'] = 'Potensial' if jumlah_cluster <= 2 else 'Paling Potensial'

        elif num_cities == 2:
            group_sorted = group.sort_values(by='total_score', ascending=False).reset_index(drop=True)
            group_sorted['Label_Cluster'] = ['Potensial', 'Tidak Potensial']
            group = group_sorted

        else:
            optimal_clusters = min(num_cities, jumlah_cluster)

            # Normalisasi dan simpan ke group sebelum diproses
            scaler = StandardScaler()
            group['total_score_normalized'] = scaler.fit_transform(group[['total_score']]).flatten()

            clustering_data = group[['total_score_normalized']].to_numpy()

            kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', max_iter=100, tol=1e-4, random_state=42)
            kmeans.fit(clustering_data)

            clusters = kmeans.labels_
            centroids = kmeans.cluster_centers_.flatten()
            centroid_labels = generate_labels_for_clusters(optimal_clusters, centroids)

            group['Cluster'] = clusters
            group['Label_Cluster'] = [centroid_labels[c] for c in clusters]

            for i, centroid in enumerate(centroids):
                group[f'Centroid_{i}'] = centroid
                group[f'Jarak_Centroid_{i}'] = np.abs(group['total_score_normalized'] - centroid)

        final_data.append(group)

    return pd.concat(final_data, ignore_index=True)




def hitung_jumlah_cluster_optimal_kota(df, score_column='total_score_normalized_city', n_cluster_options=[2, 3, 4]):
    hasil = []

    for provinsi in df['prop_sek'].unique():
        df_provinsi = df[df['prop_sek'] == provinsi]

        if score_column not in df_provinsi.columns:
            continue  # Lewati jika kolom tidak ditemukan

        X = df_provinsi[[score_column]].values
        jumlah_data = len(X)

        best_score = -1
        best_cluster = None

        for n in n_cluster_options:
            if jumlah_data > n:
                try:
                    model = KMeans(n_clusters=n, random_state=42, n_init='auto')
                    labels = model.fit_predict(X)
                    if len(set(labels)) > 1:
                        score = silhouette_score(X, labels)
                        if score > best_score:
                            best_score = score
                            best_cluster = n
                except:
                    continue

        if best_cluster:
            hasil.append({
                'prop_sek': provinsi,
                'jumlah_cluster_optimal': best_cluster,
                'skor_silhouette': round(best_score, 4)
            })
        else:
            fallback_cluster = min(jumlah_data, 2)
            hasil.append({
                'prop_sek': provinsi,
                'jumlah_cluster_optimal': fallback_cluster,
                'skor_silhouette': None
            })

    return pd.DataFrame(hasil)



# Fungsi untuk menghitung skor berbobot
@st.cache_data(show_spinner="🔢 Menghitung skor provinsi...")
# Fungsi untuk clustering provinsi berdasarkan total skor semua sekolah di provinsi tersebut
def cluster_by_province(data: pd.DataFrame, df_hash: str):
    # Group by province and calculate total score for each province
    province_data = data.groupby(['prop_sek'])['skor_akhir'].sum().reset_index(name='total_score')
    return province_data

def normalize_total_score_prov(data):
    # Inisialisasi StandardScaler
    scaler = StandardScaler()

    # Normalisasi skor akhir
    normalized_scores = scaler.fit_transform(data[['total_score']])

    # Menambahkan kolom 'total_score_normalized' ke dalam data
    data['total_score_normalized'] = normalized_scores.flatten()

    return data

@st.cache_data(show_spinner="🔢 kmeans provinsi...")
def kmeans_cluster_province(data: pd.DataFrame, optimal_clusters: int, df_hash: str):
    data = data.copy()  # pastikan tidak mengubah data asli
    # Normalisasi
    scaler = StandardScaler()
    normalized_scores = scaler.fit_transform(data[['total_score']])
    
    kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', max_iter=100, tol=1e-4, random_state=42)
    kmeans.fit(normalized_scores)

    data['Cluster'] = kmeans.labels_
    centroids = kmeans.cluster_centers_.flatten()
    data['total_score_normalized'] = normalized_scores.flatten()

    # Hitung jarak Euclidean ke setiap centroid
    for i, centroid in enumerate(centroids):
        data[f'Centroid_{i}'] = centroid
        data[f'Jarak_Centroid_{i}'] = np.abs(data['total_score_normalized'] - centroid)

    # Tambah label
    centroid_labels = generate_labels_for_clusters(optimal_clusters, kmeans.cluster_centers_.flatten())
    data['Label_Cluster'] = data['Cluster'].map(centroid_labels)
    

    # RETURN dua output: hasil cluster + centroid
    return data, kmeans.cluster_centers_.flatten()


def hitung_jumlah_cluster_optimal_provinsi(df, score_column='total_score_normalized_prov', n_cluster_options=[2, 3, 4]):
    hasil = []

    X = df[[score_column]].values
    jumlah_data = len(X)

    best_score = -1
    best_cluster = None

    for n in n_cluster_options:
        if jumlah_data > n:
            try:
                model = KMeans(n_clusters=n, random_state=42, n_init='auto')
                labels = model.fit_predict(X)
                if len(set(labels)) > 1:
                    score = silhouette_score(X, labels)
                    if score > best_score:
                        best_score = score
                        best_cluster = n
            except:
                continue

    if best_cluster:
        hasil.append({
            'jumlah_cluster_optimal': best_cluster,
            'skor_silhouette': round(best_score, 4)
        })
    else:
        fallback_cluster = min(jumlah_data, 2)
        hasil.append({
            'jumlah_cluster_optimal': fallback_cluster,
            'skor_silhouette': None
        })

    return pd.DataFrame(hasil)

# Fungsi untuk menghitung skor berbobot
@st.cache_data(show_spinner="🔢 Menghitung skor kota...")
def cluster_by_city_in_province(data: pd.DataFrame, df_hash: str):
    # Group by province and city and calculate total score for each city
    city_data = data.groupby(['prop_sek', 'kota_sek'])['skor_akhir'].sum().reset_index(name='total_score')
    return city_data

@st.cache_data(show_spinner="⏳ Menjalankan K-Means untuk kota...")
def kmeans_cluster_city(data: pd.DataFrame, jumlah_cluster: int, df_hash: str):
    final_data = []

    for provinsi, group in data.groupby('prop_sek'):
        num_cities = len(group)

        if num_cities == 1:
            group['Label_Cluster'] = 'Potensial' if jumlah_cluster <= 2 else 'Paling Potensial'

        elif num_cities == 2:
            group_sorted = group.sort_values(by='total_score', ascending=False).reset_index(drop=True)
            group_sorted['Label_Cluster'] = ['Potensial', 'Tidak Potensial']
            group = group_sorted

        else:
            optimal_clusters = min(num_cities, jumlah_cluster)

            # Normalisasi dan simpan ke group sebelum diproses
            scaler = StandardScaler()
            group['total_score_normalized'] = scaler.fit_transform(group[['total_score']]).flatten()

            clustering_data = group[['total_score_normalized']].to_numpy()

            kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', max_iter=100, tol=1e-4, random_state=42)
            kmeans.fit(clustering_data)

            clusters = kmeans.labels_
            centroids = kmeans.cluster_centers_.flatten()
            centroid_labels = generate_labels_for_clusters(optimal_clusters, centroids)

            group['Cluster'] = clusters
            group['Label_Cluster'] = [centroid_labels[c] for c in clusters]

            for i, centroid in enumerate(centroids):
                group[f'Centroid_{i}'] = centroid
                group[f'Jarak_Centroid_{i}'] = np.abs(group['total_score_normalized'] - centroid)

        final_data.append(group)

    return pd.concat(final_data, ignore_index=True)



DATA_FILE = './uploaded_files/cleaned_data.xlsx'
UPLOAD_FOLDER = 'uploaded_files'
if not os.path.exists('./uploaded_files'):
    os.makedirs('./uploaded_files')
def load_data():
    """Load the cleaned data from the main file."""
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE, engine='openpyxl')
    return pd.DataFrame()

    # Fungsi untuk mendapatkan file cleaned_data.xlsx
def get_cleaned_data_file(folder_path, file_name='cleaned_data.xlsx'):
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path):
        return file_path
    return None

# Fungsi untuk memuat data dari file Excel
def load_cleaned_data():
    file_path = get_cleaned_data_file(UPLOAD_FOLDER)
    if file_path:
        try:
            # Membaca file Excel
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            st.error(f"Error membaca file Excel: {e}")
            return pd.DataFrame()
        return df
    else:
        st.warning(f"File 'cleaned_data.xlsx' tidak ditemukan di folder '{UPLOAD_FOLDER}'.")
        return pd.DataFrame()

# Fungsi untuk menyimpan data ke file utama
def save_data(new_data):
    """Simpan data yang sudah dibersihkan ke file utama."""
    if os.path.exists(DATA_FILE):
        # Jika file sudah ada, muat data sebelumnya
        existing_data = load_data()
        # Gabungkan data yang ada dengan data baru, hilangkan duplikasi berdasarkan 'no_daftar'
        combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['no_daftar']).reset_index(drop=True)
    else:
        # Jika file belum ada, langsung simpan data baru
        combined_data = new_data

    # Simpan data gabungan ke file utama
    combined_data.to_excel(DATA_FILE, index=False, engine='openpyxl')
        # Setelah data disimpan, lakukan cache clear untuk memuat data terbaru


# Fungsi untuk menyimpan data ke file Excel
def save(data):
    data.to_excel(DATA_FILE, index=False, engine='openpyxl')
def hitung_jumlah_cluster_optimal_per_kota(df, n_cluster_options=[2, 3, 4]):
    hasil = []

    for kota in df['kota_sek'].unique():
        df_kota = df[df['kota_sek'] == kota]

        X = df_kota[['skor_akhir_normalized']].values
        jumlah_data = len(X)

        best_score = -1
        best_cluster = None

        for n in n_cluster_options:
            if jumlah_data > n:
                try:
                    model = KMeans(n_clusters=n, random_state=42, n_init='auto')
                    labels = model.fit_predict(X)
                    # Silhouette hanya valid jika hasil cluster > 1 label
                    if len(set(labels)) > 1:
                        score = silhouette_score(X, labels)
                        if score > best_score:
                            best_score = score
                            best_cluster = n
                except:
                    continue

        # Jika tidak ditemukan jumlah cluster optimal secara valid
        if best_cluster:
            hasil.append({
                'kota_sek': kota,
                'jumlah_cluster_optimal': best_cluster,
                'skor_silhouette': round(best_score, 4)
            })
        else:
            # Default: jumlah cluster optimal = jumlah data (jika 2), atau 1
            fallback_cluster = min(jumlah_data, 2)  # maks 2 agar tetap bisa dibagi dua
            hasil.append({
                'kota_sek': kota,
                'jumlah_cluster_optimal': fallback_cluster,
                'skor_silhouette': None
            })

    return pd.DataFrame(hasil)

def get_df_hash(df: pd.DataFrame) -> str:
    """Menghasilkan hash berdasarkan isi DataFrame."""
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()


@st.cache_data(show_spinner="⏳ Menjalankan K-Means untuk sekolah...")
def kmeans_per_region(data: pd.DataFrame, jumlah_cluster: int, df_hash: str):
    data = data.copy()  # pastikan tidak mengubah data asli
    data = data[data['nama_sekolah'] != 'UNKNOWN']
    
    scaler = StandardScaler()
    data['skor_akhir_normalized'] = scaler.fit_transform(data[['skor_akhir']])

    data['Cluster'] = -1
    iteration_results_schools = []

    for (provinsi, kota), group in data.groupby(['prop_sek', 'kota_sek']):
        clustering_data = group[['skor_akhir_normalized']].to_numpy()

        if len(group) < jumlah_cluster:
            clusters = np.zeros(len(group), dtype=int)
            centroids = np.array([group['skor_akhir_normalized'].mean()] * jumlah_cluster)
        else:
            kmeans = KMeans(n_clusters=jumlah_cluster, init='k-means++', max_iter=100, tol=1e-4, random_state=42)
            kmeans.fit(clustering_data)
            clusters = kmeans.labels_
            centroids = kmeans.cluster_centers_.flatten()

        centroid_labels = generate_labels_for_clusters(jumlah_cluster, centroids)

        data.loc[group.index, 'Cluster'] = clusters

        for i in range(jumlah_cluster):
            distances = np.abs(group['skor_akhir_normalized'] - centroids[i])
            data.loc[group.index, f'Centroid_{i}'] = centroids[i]
            data.loc[group.index, f'Jarak_Centroid_{i}'] = distances
        

        data.loc[group.index, 'Label_Cluster'] = [centroid_labels[cluster] for cluster in clusters]

        iteration_results_schools.append({
            "provinsi": provinsi,
            "kota": kota,
            "centroids": centroids,
            "clusters": clusters
        })

    return data, iteration_results_schools


def iconMetricContainer(key, iconUnicode, color='black'):
    """Function that returns a CSS styled container for adding a Material Icon to a Streamlit st.metric value"""
    css_style = f'''                 
                    div[data-testid="stMetricValue"]>div::before
                    {{                            
                        font-family: "Material Symbols Outlined";
                        content: "{iconUnicode}";
                        vertical-align: -20%;
                        color: {color};
                    }}                    
                    '''
    iconMetric = st.markdown(
        f'<style>{css_style}</style>',
        unsafe_allow_html=True
    )
    return iconMetric

def export_to_excel(dataframe, file_name="exported_data.xlsx"):
    # Buat file Excel dalam memori
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Sheet1")
    processed_data = output.getvalue()
    return processed_data





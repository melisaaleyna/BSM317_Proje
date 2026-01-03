#  QoS Odaklı Çok Amaçlı Rotalama Optimizasyonu

Bu proje, karmaşık ağ topolojileri üzerinde Hizmet Kalitesi parametrelerini baz alarak en iyi yol seçimini yapan meta-sezgisel bir çözüm sunar. 250 düğümlü bir ağ üzerinde **Genetik Algoritma (GA)** ve **Karınca Kolonisi Optimizasyonu (ACO)** algoritmalarını yarıştırır.

##  Öne Çıkan Özellikler
- **Modern Arayüz:** Flask tabanlı backend ve vis-network.js ile geliştirilmiş interaktif Cyberpunk dashboard.
- **Çok Amaçlı Optimizasyon:** Gecikme, Güvenilirlik ve Kaynak Kullanımı metriklerinin ağırlıklı toplam (Weighted Sum) ile optimizasyonu.
- **Akıllı Topoloji:** Erdős-Rényi modeli ile üretilen ve bağlantı garantisi sunan ağ yapısı.
- **Otomatik Deney Sistemi:** 20 farklı senaryo üzerinden istatistiksel analiz ve raporlama.

##  Kurulum ve Çalıştırma

### 1. Gereksinimler
Projeyi çalıştırmak için Python 3.8+ gereklidir. Önce bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt

"""
Lazer Atış Tespit Sistemi - Ana Giriş Noktası

Bu program, kamera ile lazer tabanca atışlarını gerçek zamanlı olarak tespit eden,
isabetliliği değerlendiren ve kayıt altına alan bir görüntü işleme uygulamasıdır.

Özellikler:
- Gerçek zamanlı kırmızı lazer tespiti
- Multi-threading ile yüksek performans
- Atış geçmişi kaydetme/yükleme
- Hedef bölgesi tanımlama
- Kamera perspektif düzeltme
- Çift ekran desteği (kontrol + hedef penceresi)

Kullanılan Teknolojiler:
- PyQt5: GUI framework
- OpenCV: Görüntü işleme
- NumPy: Sayısal hesaplamalar
"""

# PyQt5 widget modülü - GUI bileşenleri için
from PyQt5 import QtWidgets

# Ana kullanıcı arayüzü sınıfı
from modules.main.main_ui import MainUI

# Program buradan başlar
if __name__ == "__main__":
    # Sistem argümanları için (command line parametreleri)
    import sys

    # PyQt5 uygulaması oluştur (sys.argv ile komut satırı argümanlarını geç)
    app = QtWidgets.QApplication(sys.argv)
    
    # Ana pencereyi oluştur ve göster
    # MainUI constructor içinde otomatik olarak show() çağrılıyor
    ui = MainUI()
    
    # Uygulama event loop'unu başlat ve çıkış kodunu döndür
    # Kullanıcı pencereyi kapattığında program düzgün şekilde sonlanır
    sys.exit(app.exec_())

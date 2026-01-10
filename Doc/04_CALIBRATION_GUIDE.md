# 🎯 Kalibrasyon Kılavuzu

Bu dokümanda fiziksel ekran ve kamera arasındaki kalibrasyon sürecinin detayları yer almaktadır.

---

## 📋 Kalibrasyon Neden Gerekli?

Fiziksel dünyadan dijital dünyaya doğru koordinat aktarımı için:

| Problem | Açıklama |
|---------|----------|
| **Perspektif Bozulması** | Kamera ekrana dik bakmıyor olabilir |
| **Lens Distorsiyonu** | Kamera lensi görüntüyü bükebilir |
| **Konum Farklılığı** | Kamera ekranın tam karşısında olmayabilir |
| **Çözünürlük Uyumsuzluğu** | Kamera ve hedef ekran farklı çözünürlükte |

---

## 🔧 Kalibrasyon Yöntemleri

### 1️⃣ Manuel 4-Köşe Kalibrasyonu (Mevcut Sistem)

**Nasıl Çalışır:**
1. Kullanıcı ekranın 4 köşesini kamera görüntüsünde işaretler
2. Homography matrisi hesaplanır
3. Tüm koordinatlar bu matris ile dönüştürülür

**Avantajlar:**
- Basit implementasyon
- Hızlı kurulum

**Dezavantajlar:**
- Her kurulumda tekrar gerekiyor
- İnsan hatası riski

```
Kamera Görüntüsü              Düzeltilmiş Görüntü
+------------------+          +------------------+
|    *TL      TR*  |          |*TL            TR*|
|      +----+      |   ===>   |                  |
|      |    |      |          |                  |
|    *BL      BR*  |          |*BL            BR*|
+------------------+          +------------------+
```

---

### 2️⃣ ArUco Marker Kalibrasyonu (Önerilen)

**Nasıl Çalışır:**
1. Ekran köşelerine ArUco marker'lar yerleştirilir
2. OpenCV otomatik olarak marker'ları tespit eder
3. Marker pozisyonlarından kalibrasyon matrisi oluşturulur

**Avantajlar:**
- Otomatik köşe tespiti
- Dinamik güncelleme mümkün
- Yüksek hassasiyet

**Dezavantajlar:**
- Marker'lar görünür olmalı
- Ek kurulum gerektirir

**ArUco Marker Örneği:**
```
+---+  +---+
|0 1|  |0 1|
|1 0|  |1 1|
+---+  +---+
 ID:0   ID:1
```

---

### 3️⃣ Checkerboard Kalibrasyonu (Lens Düzeltme)

**Nasıl Çalışır:**
1. Satranç tahtası deseni kameraya gösterilir
2. OpenCV iç köşeleri tespit eder
3. Lens distorsiyon katsayıları hesaplanır

**Kullanım Alanı:**
- Geniş açılı kameralarda lens bükülmesi düzeltme
- Profesyonel kalibrasyon gerektiren durumlar

---

## 📐 Kalibrasyon Adımları

### Adım 1: Fiziksel Kurulum

```
[Lazer Atış Bölgesi]
         |
         v
+-------------------+
|                   |
|    FİZİKSEL       |  <-- Projeksiyon veya monitör
|      EKRAN        |
|                   |
+-------------------+
         ^
         |
    [KAMERA]  <-- Ekrana bakacak şekilde konumlandır
```

**Dikkat Edilecekler:**
- Kamera mümkünse ekrana dik baksın
- Tüm ekran kamera görüntüsünde yer alsın
- Ortam ışığı kontrol altında olsun (IR tercih edilir)

---

### Adım 2: Yazılım Kalibrasyonu

#### A) Manuel Kalibrasyon (Mevcut)

1. Uygulamayı başlat
2. Menü → Operations → Camera Calibration
3. Ekranın 4 köşesini sırasıyla tıkla:
   - Sol Üst (TL)
   - Sağ Üst (TR)
   - Sağ Alt (BR)
   - Sol Alt (BL)
4. Kalibrasyon tamamlandı

#### B) ArUco Kalibrasyon (Gelecek)

1. ArUco marker'ları yazdır ve ekran köşelerine yerleştir
2. Uygulamayı başlat
3. Menü → Operations → Auto Calibration
4. Sistem otomatik olarak marker'ları tespit eder
5. Kalibrasyon tamamlandı

---

### Adım 3: Doğrulama

Kalibrasyonu test etmek için:

1. Ekranın bilinen noktalarına lazer tut
2. Tespit edilen koordinatları kontrol et
3. Sapma varsa tekrar kalibre et

**Hedef Sapma Değerleri:**
| Bölge | Kabul Edilebilir Sapma |
|-------|------------------------|
| Merkez | < 5 piksel |
| Köşeler | < 10 piksel |
| Kenarlar | < 8 piksel |

---

## 🧮 Matematiksel Arka Plan

### Homography Matrisi

2D perspektif dönüşümü için 3x3 matris kullanılır:

```
| x' |   | h11  h12  h13 |   | x |
| y' | = | h21  h22  h23 | * | y |
| w' |   | h31  h32  h33 |   | 1 |

Sonuç: (x'/w', y'/w')
```

### OpenCV Kullanımı

```python
import cv2
import numpy as np

# Kaynak noktalar (kamera görüntüsündeki köşeler)
src_points = np.float32([
    [100, 50],   # TL
    [540, 80],   # TR
    [520, 400],  # BR
    [80, 380]    # BL
])

# Hedef noktalar (düzeltilmiş dikdörtgen)
dst_points = np.float32([
    [0, 0],
    [640, 0],
    [640, 480],
    [0, 480]
])

# Homography matrisi hesapla
matrix = cv2.getPerspectiveTransform(src_points, dst_points)

# Görüntüyü dönüştür
warped = cv2.warpPerspective(frame, matrix, (640, 480))

# Tek bir noktayı dönüştür
point = np.float32([[300, 200]])
transformed = cv2.perspectiveTransform(point.reshape(1, -1, 2), matrix)
```

---

## 🔄 Dinamik Kalibrasyon

Sistem çalışırken kalibrasyonu güncellemek için:

### Seçenek 1: Periyodik Yenileme

```python
class DynamicCalibrator:
    def __init__(self, refresh_interval=60):  # 60 saniyede bir
        self.interval = refresh_interval
        self.last_update = time.time()
    
    def check_and_update(self, frame):
        if time.time() - self.last_update > self.interval:
            markers = self.detect_markers(frame)
            if len(markers) == 4:
                self.update_calibration(markers)
                self.last_update = time.time()
```

### Seçenek 2: Güven Skorlu Güncelleme

```python
class ConfidenceCalibrator:
    def __init__(self, confidence_threshold=0.9):
        self.threshold = confidence_threshold
    
    def should_recalibrate(self, detection_confidence):
        # Tespit güveni düşükse yeniden kalibre et
        return detection_confidence < self.threshold
```

---

## 📝 Kalibrasyon Dosya Formatı

### calibration.json

```json
{
    "version": "1.0",
    "timestamp": "2026-01-10T12:30:00",
    "camera": {
        "device_id": 0,
        "resolution": [1280, 720]
    },
    "screen": {
        "resolution": [1920, 1080]
    },
    "calibration": {
        "source_points": [
            [120, 45],
            [1150, 52],
            [1140, 695],
            [115, 688]
        ],
        "destination_points": [
            [0, 0],
            [1920, 0],
            [1920, 1080],
            [0, 1080]
        ],
        "matrix": [
            [1.523, 0.021, -180.5],
            [0.015, 1.498, -65.2],
            [0.00001, 0.00002, 1.0]
        ]
    },
    "lens_correction": {
        "enabled": false,
        "distortion_coefficients": [],
        "camera_matrix": []
    }
}
```

---

## ⚠️ Sık Karşılaşılan Sorunlar

### 1. Köşeler Tespit Edilemiyor

**Belirtiler:** ArUco marker'lar algılanmıyor

**Çözümler:**
- Aydınlatmayı kontrol et
- Marker boyutunu büyüt
- Kamera odaklama ayarını kontrol et

### 2. Perspektif Düzeltme Yanlış

**Belirtiler:** Dönüştürülen koordinatlar tutarsız

**Çözümler:**
- Köşeleri doğru sırada işaretle (TL→TR→BR→BL)
- Kamera pozisyonunu değiştir
- Lens distorsiyon düzeltmesi ekle

### 3. Lazer Tespiti Tutarsız

**Belirtiler:** Bazı atışlar algılanmıyor

**Çözümler:**
- Ortam ışığını azalt
- IR kamera kullan
- HSV eşik değerlerini ayarla

---

## 🎯 İleri Seviye: Kamera-Ekran Senkronizasyonu

Unreal Engine ekranı ile fiziksel ekran arasında senkronizasyon:

```
Unreal Kamera Pozisyonu  <──>  Fiziksel Kamera Pozisyonu
         │                              │
         ▼                              ▼
   Unreal Ekranı          ==      Fiziksel Ekran
         │                              │
         ▼                              ▼
  3D World Position      <──>   2D Screen Position
```

Bu senkronizasyon için:
1. Unreal'daki sabit kameranın FOV'u bilinmeli
2. Fiziksel ekran boyutu bilinmeli
3. Kamera-ekran mesafesi hesaplanmalı

---

*Son Güncelleme: 10 Ocak 2026*

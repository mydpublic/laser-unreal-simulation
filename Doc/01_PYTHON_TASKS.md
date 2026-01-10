# 🐍 Python Geliştirme Planı

## 📋 Mevcut Durum

### ✅ Tamamlanan Özellikler
- Kamera yakalama ve frame işleme (`camera.py`)
- Lazer tespiti - HSV renk analizi (`detection.py`)
- Perspektif düzeltme - Homography (`perspective.py`)
- Hedef bölgesi tanımlama (`feat.py`)
- PyQt5 GUI arayüzü (`main_ui.py`, `target.py`)
- Multi-threading desteği

### ⚠️ Eksik/İyileştirilecek Özellikler
- Socket iletişim modülü (YOK)
- Normalize koordinat çıktısı (Pixel bazlı → 0-1 arası)
- Gelişmiş kalibrasyon sistemi
- Konfigürasyon dosyası (JSON/YAML)

---

## 🔧 Yapılacak Geliştirmeler

### 1️⃣ Socket İletişim Modülü (Öncelik: YÜKSEK)

**Dosya:** `modules/common/network.py`

```python
# Hedef API Tasarımı
class LaserSocketClient:
    def __init__(self, host: str, port: int, protocol: str = "UDP"):
        """
        Unreal Engine'a bağlanacak socket client.
        
        Args:
            host: Unreal çalışan bilgisayar IP'si (genelde localhost)
            port: Dinleme portu (önerilen: 7777)
            protocol: "UDP" (düşük gecikme) veya "TCP" (güvenilir)
        """
        pass
    
    def send_coordinates(self, x: float, y: float, timestamp: float = None):
        """
        Normalize edilmiş koordinatları gönderir.
        
        Args:
            x: 0.0 - 1.0 arası yatay pozisyon
            y: 0.0 - 1.0 arası dikey pozisyon
            timestamp: Opsiyonel zaman damgası
        """
        pass
    
    def send_hit_event(self, x: float, y: float, confidence: float):
        """
        Tespit edilen atış olayını gönderir.
        
        Args:
            x, y: Normalize koordinatlar
            confidence: Tespit güvenilirliği (0.0 - 1.0)
        """
        pass
```

**Mesaj Formatı (JSON):**
```json
{
    "type": "laser_hit",
    "x": 0.534,
    "y": 0.721,
    "timestamp": 1704873600.123,
    "confidence": 0.95
}
```

---

### 2️⃣ Koordinat Normalizasyonu (Öncelik: YÜKSEK)

**Dosya:** `modules/common/detection.py` - Güncelleme

Mevcut `detect()` fonksiyonu pixel bazlı koordinat döndürüyor.
Bunu 0-1 arası normalize değere çevirmemiz gerekiyor.

```python
# Mevcut
def detect(self, image):
    # ... tespit kodu ...
    return [(x, y), ...]  # Pixel koordinatları

# Hedef
def detect(self, image, normalize: bool = True):
    # ... tespit kodu ...
    if normalize:
        height, width = image.shape[:2]
        return [(x / width, y / height), ...]  # 0-1 arası
    return [(x, y), ...]
```

---

### 3️⃣ Gelişmiş Kalibrasyon Sistemi (Öncelik: ORTA)

**Yeni Dosya:** `modules/calibration/screen_calibrator.py`

```python
class ScreenCalibrator:
    """
    Ekran köşe noktalarının otomatik/manuel tespiti.
    4 köşe noktası ile perspektif dönüşüm matrisi oluşturur.
    """
    
    def __init__(self):
        self.corners = []  # [TL, TR, BR, BL]
        self.matrix = None
    
    def auto_detect_corners(self, frame):
        """
        ArUco marker veya renk tespiti ile köşeleri otomatik bulur.
        """
        pass
    
    def manual_calibration(self, callback):
        """
        Kullanıcının 4 köşeyi tıklamasını bekler.
        """
        pass
    
    def save_calibration(self, filepath: str):
        """Kalibrasyon verilerini JSON olarak kaydeder."""
        pass
    
    def load_calibration(self, filepath: str):
        """Kaydedilmiş kalibrasyonu yükler."""
        pass
```

---

### 4️⃣ Konfigürasyon Sistemi (Öncelik: ORTA)

**Yeni Dosya:** `config.json`

```json
{
    "camera": {
        "device_id": 0,
        "width": 1280,
        "height": 720,
        "fps": 60
    },
    "detection": {
        "hsv_lower_red_1": [0, 20, 20],
        "hsv_upper_red_1": [10, 255, 255],
        "hsv_lower_red_2": [160, 20, 20],
        "hsv_upper_red_2": [180, 255, 255],
        "min_contour_area": 10,
        "detection_delay_ms": 250
    },
    "network": {
        "host": "127.0.0.1",
        "port": 7777,
        "protocol": "UDP"
    },
    "calibration": {
        "auto_load": true,
        "file_path": "calibration.json"
    }
}
```

**Yeni Dosya:** `modules/common/config.py`

```python
import json
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class CameraConfig:
    device_id: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 60

@dataclass
class DetectionConfig:
    hsv_lower_red_1: Tuple[int, int, int] = (0, 20, 20)
    hsv_upper_red_1: Tuple[int, int, int] = (10, 255, 255)
    # ... diğer ayarlar

@dataclass
class NetworkConfig:
    host: str = "127.0.0.1"
    port: int = 7777
    protocol: str = "UDP"

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.camera = CameraConfig()
        self.detection = DetectionConfig()
        self.network = NetworkConfig()
        self.load(config_path)
    
    def load(self, path: str):
        """JSON dosyasından konfigürasyon yükler."""
        pass
    
    def save(self, path: str):
        """Konfigürasyonu JSON dosyasına kaydeder."""
        pass
```

---

### 5️⃣ Entegrasyon - CameraWork Güncelleme (Öncelik: YÜKSEK)

**Dosya:** `modules/common/camera.py`

```python
# Eklenecek import
from modules.common.network import LaserSocketClient

class CameraWork(QObject):
    def __init__(self, camera_id=...):
        super().__init__()
        # ... mevcut kod ...
        
        # 🆕 Socket client
        self.__socket_client = LaserSocketClient(
            host="127.0.0.1",
            port=7777,
            protocol="UDP"
        )
    
    def run(self):
        # ... mevcut kod ...
        
        while self.isWorkerAlive:
            # ... tespit kodu ...
            
            if len(points) > 0:
                # 🆕 Normalize koordinatları Unreal'a gönder
                x_norm = points[0][0] / self.available_width
                y_norm = points[0][1] / self.available_height
                self.__socket_client.send_hit_event(x_norm, y_norm, confidence=0.9)
```

---

## 📝 Görev Listesi

### Faz 1: İletişim Altyapısı
- [x] `network.py` modülünü oluştur ✅
- [x] UDP socket client implementasyonu ✅
- [x] TCP fallback desteği ✅
- [x] Bağlantı durumu kontrolü (heartbeat) ✅
- [x] Hata yönetimi ve reconnect ✅

### Faz 2: Koordinat İyileştirme
- [x] `detection.py` - normalize parametre ekle ✅
- [ ] Koordinat smoothing (jitter azaltma)
- [ ] Multi-point tracking desteği
- [ ] Confidence score hesaplama

### Faz 3: Konfigürasyon
- [x] `constants.py` - NetworkConstants eklendi ✅
- [ ] `config.json` şablonu oluştur
- [ ] `config.py` - ConfigManager sınıfı
- [ ] GUI'de ayarlar paneli
- [ ] Çalışma zamanı ayar değişikliği

### Faz 4: Kalibrasyon
- [ ] `screen_calibrator.py` modülü
- [ ] ArUco marker desteği
- [ ] Otomatik köşe tespiti
- [ ] Kalibrasyon kaydet/yükle

### Faz 5: Test & Optimizasyon
- [ ] Birim testler
- [ ] Performans profiling
- [ ] Gecikme ölçümü (<50ms hedef)
- [ ] Memory leak kontrolü

---

## 🔗 Bağımlılıklar

```
# requirements.txt güncellemesi
opencv-python>=4.5.0
numpy>=1.21.0
PyQt5>=5.15.0
pyqt5-tools>=5.15.0

# 🆕 Yeni bağımlılıklar
dataclasses-json>=0.5.0    # Konfigürasyon için
opencv-contrib-python>=4.5.0  # ArUco marker için (opsiyonel)
```

---

*Son Güncelleme: 10 Ocak 2026*

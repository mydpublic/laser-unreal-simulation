# 🎯 Lazer Atış Simülasyon Sistemi - Proje Dokümantasyonu

## 📋 Proje Özeti

Bu proje, gerçek dünyada kullanılan bir **lazer işaretleyici** ile fiziksel bir ekrana yapılan atışın,
kamera ve görüntü işleme yardımıyla algılanarak, **Unreal Engine** içerisindeki 3D bir simülasyon ortamına
doğru ve gerçekçi şekilde aktarılmasını hedefler.

### 🎯 Temel Hedefler
- Fiziksel-dijital etkileşim (fare/dokunmatik yerine gerçek lazer)
- Gerçek zamanlı koordinat aktarımı
- 3D sahnede doğru açı/mesafe/perspektif hesaplaması
- Karakterlerin vuruş bölgesine göre tepki vermesi

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DONANIM KATMANI                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Lazer İşaretleyici] ──▶ [Fiziksel Ekran] ◀── [IR/Normal Kamera]          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      GÖRÜNTÜ İŞLEME KATMANI (Python)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Kamera Yakalama] ──▶ [Lazer Tespiti] ──▶ [Perspektif Düzeltme]           │
│         │                    │                      │                       │
│         ▼                    ▼                      ▼                       │
│  [Frame Buffer]      [HSV + Contour]      [Homography Matrix]              │
│                              │                      │                       │
│                              └──────────┬───────────┘                       │
│                                         ▼                                   │
│                              [Normalize Koordinat]                          │
│                                   (0.0 - 1.0)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ TCP/UDP Socket
┌─────────────────────────────────────────────────────────────────────────────┐
│                      UNREAL ENGINE KATMANI (C++)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Socket Receiver] ──▶ [Coordinate Transformer] ──▶ [Line Trace System]   │
│         │                       │                          │                │
│         ▼                       ▼                          ▼                │
│  [Async Thread]         [Screen to World]          [Ray Cast]              │
│                                                            │                │
│                                                            ▼                │
│                                                   [Hit Detection]           │
│                                                            │                │
│                                    ┌───────────────────────┼────────────┐   │
│                                    ▼                       ▼            ▼   │
│                              [Head Hit]            [Body Hit]    [Limb Hit] │
│                                    │                       │            │   │
│                                    ▼                       ▼            ▼   │
│                              [Stun Anim]           [Knockback]    [Stumble] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Proje Dosya Yapısı (Hedef)

```
laser-unreal-simulation/
├── Doc/                           # 📚 Dokümantasyon
│   ├── README.md                  # Bu dosya
│   ├── 01_PYTHON_TASKS.md         # Python geliştirme planı
│   ├── 02_UNREAL_TASKS.md         # Unreal geliştirme planı
│   ├── 03_CPP_INTEGRATION.md      # C++ entegrasyon detayları
│   └── 04_CALIBRATION_GUIDE.md    # Kalibrasyon kılavuzu
│
├── Python/
│   └── atis_sistemi/
│       ├── main.py
│       └── modules/
│           ├── common/
│           │   ├── camera.py
│           │   ├── detection.py
│           │   ├── constants.py
│           │   └── network.py      # 🆕 Socket iletişim modülü
│           ├── calibration/        # 🆕 Gelişmiş kalibrasyon
│           │   ├── screen_calibrator.py
│           │   └── perspective_mapper.py
│           └── ...
│
├── Unreal/
│   └── unrealproject1 5.7/
│       └── Source/                 # 🆕 C++ kaynak kodları
│           ├── LaserReceiver/
│           │   ├── LaserSocketReceiver.h
│           │   └── LaserSocketReceiver.cpp
│           ├── LaserTrace/
│           │   ├── LaserTraceActor.h
│           │   └── LaserTraceActor.cpp
│           └── HitReaction/
│               ├── HitReactionComponent.h
│               └── HitReactionComponent.cpp
│
└── Scripts/                        # 🆕 Yardımcı scriptler
    ├── run_python.bat
    ├── build_unreal.bat
    └── test_connection.py
```

---

## 🔄 Geliştirme Fazları

### Faz 1: Temel İletişim (1-2 hafta)
- [ ] Python socket server modülü
- [ ] Unreal C++ socket client
- [ ] Basit koordinat gönderimi testi

### Faz 2: Koordinat Dönüşümü (1-2 hafta)
- [ ] Python'da normalize koordinat çıktısı
- [ ] Unreal'da Screen-to-World dönüşümü
- [ ] Sabit kamera sistemi kurulumu

### Faz 3: Line Trace Sistemi (1 hafta)
- [ ] C++ LineTrace Actor
- [ ] Debug görselleştirme
- [ ] Hit result işleme

### Faz 4: Karakter Tepki Sistemi (2-3 hafta)
- [ ] Skeletal mesh hit detection
- [ ] Bone-based vuruş tespiti
- [ ] Animation Blueprint entegrasyonu
- [ ] Tepki animasyonları

### Faz 5: Kalibrasyon & İyileştirme (1 hafta)
- [ ] Otomatik ekran köşe tespiti
- [ ] Dinamik perspektif düzeltme
- [ ] Performans optimizasyonu

---

## 📊 Teknik Gereksinimler

### Donanım
| Bileşen | Minimum | Önerilen |
|---------|---------|----------|
| Kamera | 30 FPS, 480p | 60+ FPS, 720p IR |
| Ekran | 1080p | 4K |
| GPU | GTX 1060 | RTX 3070+ (Ray Tracing) |

### Yazılım
| Bileşen | Versiyon |
|---------|----------|
| Python | 3.9+ |
| OpenCV | 4.5+ |
| PyQt5 | 5.15+ |
| Unreal Engine | 5.7 |
| Visual Studio | 2022 |

---

## 📝 Notlar

- IR kamera kullanımı, ortam ışığından bağımsız tespit sağlar
- UDP tercih edilir (düşük gecikme), TCP yedek olarak tutulabilir
- Unreal'da Dedicated Server yerine Listen Server modeli yeterli
- Frame buffer ile gecikme 16-33ms aralığında tutulmalı

---

*Son Güncelleme: 10 Ocak 2026*

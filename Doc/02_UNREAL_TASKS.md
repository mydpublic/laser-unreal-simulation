# 🎮 Unreal Engine Geliştirme Planı

## 📋 Mevcut Durum

### ✅ Mevcut Özellikler
- Unreal Engine 5.7 projesi
- Third Person şablonu
- Ray Tracing, Lumen GI aktif
- Temel karakter ve sahne

### ❌ Eksik Özellikler
- C++ Source dosyaları (Blueprint-only proje)
- Socket iletişim sistemi
- Sabit kamera sistemi
- Line Trace mekanizması
- Hit detection sistemi
- Karakter tepki sistemi

---

## 🏗️ Sistem Bileşenleri

### 1️⃣ Socket Receiver Sistemi

Python'dan gelen lazer koordinatlarını almak için asenkron socket listener.

**Bileşenler:**
- `ALaserSocketReceiver` - Actor sınıfı
- UDP/TCP socket dinleyici
- Thread-safe mesaj kuyruğu
- Event dispatcher

**İş Akışı:**
```
Python ──UDP──▶ [Socket Thread] ──▶ [Message Queue] ──▶ [Game Thread] ──▶ [Event]
                     │                    │                    │
                 Async I/O           Thread-safe            Tick()
```

---

### 2️⃣ Coordinate Transformer

Ekran koordinatlarını 3D dünya koordinatlarına çevirir.

**Bileşenler:**
- `UCoordinateTransformer` - UObject sınıfı
- Screen-to-World projeksiyon
- Kamera perspektif hesaplaması

**Matematiksel Dönüşüm:**
```
Girdi:  ScreenX (0-1), ScreenY (0-1)
        ↓
        DeprojectScreenToWorld(ScreenPos, WorldPos, WorldDir)
        ↓
Çıktı:  WorldLocation, WorldDirection (Ray başlangıç ve yönü)
```

---

### 3️⃣ Sabit Kamera Sistemi

Lazer atışlarının referans alacağı sabit kamera.

**Özellikler:**
- Sabit pozisyon ve rotasyon
- Ayarlanabilir FOV
- Sahneyi kaplayan görüş alanı
- Debug görselleştirme

---

### 4️⃣ Line Trace (Ray Cast) Sistemi

Kameradan hedefe doğru ışın fırlatma.

**Bileşenler:**
- `ALaserTraceActor` - Ana trace aktörü
- Multi-channel trace desteği
- Debug çizim (görsel ray)

**Trace Tipleri:**
```cpp
// Visibility - Görünürlük kontrolü
ECC_Visibility

// Pawn - Karakter çarpışması
ECC_Pawn

// Custom - Özel kanal (LaserHit)
ECC_GameTraceChannel1
```

---

### 5️⃣ Hit Detection Sistemi

Vuruş noktası ve bone tespiti.

**Bileşenler:**
- `UHitReactionComponent` - ActorComponent
- Skeletal mesh bone tespiti
- Hit bölgesi sınıflandırma

**Bone Grupları:**
| Grup | Bone İsimleri | Tepki Tipi |
|------|---------------|------------|
| Head | head, neck | Stun |
| Torso | spine_01, spine_02, spine_03 | Knockback |
| Arm_L | upperarm_l, lowerarm_l, hand_l | Flinch |
| Arm_R | upperarm_r, lowerarm_r, hand_r | Flinch |
| Leg_L | thigh_l, calf_l, foot_l | Stumble |
| Leg_R | thigh_r, calf_r, foot_r | Stumble |

---

### 6️⃣ Karakter Tepki Sistemi

Vuruşa göre animasyon ve fizik tepkisi.

**Bileşenler:**
- Animation Blueprint güncellemesi
- Anim Montage'lar
- Physical Animation (opsiyonel)
- Ragdoll sistemi (opsiyonel)

**Tepki Tipleri:**
```
Head Hit    → Stun (baş sallama, dengesizlik)
Torso Hit   → Knockback (geri itilme)
Arm Hit     → Flinch (kolu çekme)
Leg Hit     → Stumble (sendeleme)
Critical    → Ragdoll (yere düşme)
```

---

## 📁 Dosya Yapısı

```
Source/unrealproject1/
├── unrealproject1.Build.cs           # Build konfigürasyonu
├── unrealproject1.h                  # Ana header
├── unrealproject1.cpp                # Ana source
│
├── Network/
│   ├── LaserSocketReceiver.h
│   ├── LaserSocketReceiver.cpp
│   └── LaserMessage.h                # Mesaj struct'ları
│
├── LaserSystem/
│   ├── LaserTraceActor.h
│   ├── LaserTraceActor.cpp
│   ├── CoordinateTransformer.h
│   └── CoordinateTransformer.cpp
│
├── HitReaction/
│   ├── HitReactionComponent.h
│   ├── HitReactionComponent.cpp
│   ├── HitZoneTypes.h                # Enum ve struct'lar
│   └── ReactionAnimationData.h       # Animasyon veri varlıkları
│
└── Camera/
    ├── LaserCameraActor.h
    └── LaserCameraActor.cpp
```

---

## 🎨 Blueprint Entegrasyonu

### BP_LaserGameMode
- LaserSocketReceiver spawn
- Sabit kamera referansı
- Oyun başlangıç ayarları

### BP_LaserCharacter (ThirdPersonCharacter güncelleme)
- HitReactionComponent ekleme
- Animation Blueprint bağlantısı
- Health/Damage sistemi (opsiyonel)

### ABP_LaserCharacter (Animation Blueprint)
- Hit reaction state machine
- Blend poses
- Anim notify events

---

## 📝 Görev Listesi

### Faz 1: Proje Kurulumu
- [ ] C++ proje dönüşümü (Source klasörü oluştur)
- [ ] Build.cs dosyası - Networking modülü ekle
- [ ] Temel sınıfları oluştur
- [ ] Hot Reload test

### Faz 2: Socket İletişim
- [ ] LaserSocketReceiver Actor oluştur
- [ ] UDP listener implementasyonu
- [ ] Async thread yönetimi
- [ ] JSON parse (FJsonObject)
- [ ] Blueprint event dispatcher
- [ ] Bağlantı test

### Faz 3: Kamera & Koordinat
- [ ] LaserCameraActor oluştur
- [ ] Sabit pozisyon sistemi
- [ ] CoordinateTransformer implementasyonu
- [ ] DeprojectScreenToWorld entegrasyonu
- [ ] Debug görselleştirme

### Faz 4: Line Trace
- [ ] LaserTraceActor oluştur
- [ ] LineTraceSingleByChannel implementasyonu
- [ ] Custom trace channel (LaserHit)
- [ ] Debug draw (DrawDebugLine)
- [ ] Hit result işleme

### Faz 5: Hit Detection
- [ ] HitReactionComponent oluştur
- [ ] Bone name mapping
- [ ] Hit zone sınıflandırma
- [ ] Blueprint olayları

### Faz 6: Karakter Tepki
- [ ] Reaction montage'ları import/oluştur
- [ ] Animation Blueprint state machine
- [ ] Hit → Animation bağlantısı
- [ ] Physical animation (opsiyonel)
- [ ] Ragdoll sistemi (opsiyonel)

### Faz 7: Polish & Test
- [ ] Gecikme optimizasyonu
- [ ] Görsel efektler (lazer beam, hit particle)
- [ ] Ses efektleri
- [ ] Multiplayer desteği (opsiyonel)

---

## ⚙️ Build Konfigürasyonu

### unrealproject1.Build.cs
```csharp
using UnrealBuildTool;

public class unrealproject1 : ModuleRules
{
    public unrealproject1(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] { 
            "Core", 
            "CoreUObject", 
            "Engine", 
            "InputCore",
            "Sockets",           // 🆕 Socket iletişim
            "Networking",        // 🆕 Network utilities
            "Json",              // 🆕 JSON parse
            "JsonUtilities"      // 🆕 JSON utilities
        });

        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
```

---

## 🔗 Unreal Engine Referanslar

- [Networking and Multiplayer](https://docs.unrealengine.com/5.3/en-US/networking-and-multiplayer-in-unreal-engine/)
- [Line Traces](https://docs.unrealengine.com/5.3/en-US/traces-in-unreal-engine/)
- [Animation Blueprints](https://docs.unrealengine.com/5.3/en-US/animation-blueprints-in-unreal-engine/)
- [Skeletal Mesh Components](https://docs.unrealengine.com/5.3/en-US/skeletal-mesh-components-in-unreal-engine/)

---

*Son Güncelleme: 10 Ocak 2026*

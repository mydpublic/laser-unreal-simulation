# 🔧 C++ Entegrasyon Detayları

Bu dokümanda Unreal Engine C++ sınıflarının detaylı implementasyonu yer almaktadır.

---

## 1️⃣ LaserSocketReceiver - Socket İletişim

### Header Dosyası

```cpp
// LaserSocketReceiver.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Sockets.h"
#include "SocketSubsystem.h"
#include "Common/UdpSocketBuilder.h"
#include "Common/UdpSocketReceiver.h"
#include "LaserSocketReceiver.generated.h"

// Lazer vuruş olayı için delegate
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnLaserHitReceived, float, X, float, Y, float, Confidence);

UCLASS()
class UNREALPROJECT1_API ALaserSocketReceiver : public AActor
{
    GENERATED_BODY()
    
public:    
    ALaserSocketReceiver();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

    // Blueprint'ten erişilebilir event
    UPROPERTY(BlueprintAssignable, Category = "Laser")
    FOnLaserHitReceived OnLaserHitReceived;

    // Ayarlar
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Network")
    int32 ListenPort = 7777;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Network")
    FString ListenIP = TEXT("0.0.0.0");

    // Bağlantı durumu
    UPROPERTY(BlueprintReadOnly, Category = "Network")
    bool bIsConnected = false;

protected:
    // Socket bileşenleri
    FSocket* Socket;
    FUdpSocketReceiver* UDPReceiver;
    
    // Thread-safe mesaj kuyruğu
    TQueue<FString, EQueueMode::Mpsc> MessageQueue;

    // Socket başlat
    bool StartListening();
    
    // Socket durdur
    void StopListening();
    
    // Mesaj alındığında çağrılır (farklı thread)
    void OnDataReceived(const FArrayReaderPtr& Data, const FIPv4Endpoint& Endpoint);
    
    // Mesajı işle (game thread)
    void ProcessMessage(const FString& Message);
};
```

### Source Dosyası

```cpp
// LaserSocketReceiver.cpp
#include "LaserSocketReceiver.h"
#include "Async/Async.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

ALaserSocketReceiver::ALaserSocketReceiver()
{
    PrimaryActorTick.bCanEverTick = true;
    Socket = nullptr;
    UDPReceiver = nullptr;
}

void ALaserSocketReceiver::BeginPlay()
{
    Super::BeginPlay();
    StartListening();
}

void ALaserSocketReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopListening();
    Super::EndPlay(EndPlayReason);
}

bool ALaserSocketReceiver::StartListening()
{
    // Socket oluştur
    FIPv4Address IP;
    FIPv4Address::Parse(ListenIP, IP);
    FIPv4Endpoint Endpoint(IP, ListenPort);

    Socket = FUdpSocketBuilder(TEXT("LaserSocket"))
        .AsNonBlocking()
        .AsReusable()
        .BoundToEndpoint(Endpoint)
        .WithReceiveBufferSize(2 * 1024 * 1024);

    if (!Socket)
    {
        UE_LOG(LogTemp, Error, TEXT("LaserSocket: Failed to create socket!"));
        return false;
    }

    // Receiver başlat
    UDPReceiver = new FUdpSocketReceiver(
        Socket,
        FTimespan::FromMilliseconds(100),
        TEXT("LaserUDPReceiver")
    );
    
    UDPReceiver->OnDataReceived().BindUObject(this, &ALaserSocketReceiver::OnDataReceived);
    UDPReceiver->Start();

    bIsConnected = true;
    UE_LOG(LogTemp, Log, TEXT("LaserSocket: Listening on port %d"), ListenPort);
    return true;
}

void ALaserSocketReceiver::StopListening()
{
    if (UDPReceiver)
    {
        UDPReceiver->Stop();
        delete UDPReceiver;
        UDPReceiver = nullptr;
    }

    if (Socket)
    {
        Socket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(Socket);
        Socket = nullptr;
    }

    bIsConnected = false;
    UE_LOG(LogTemp, Log, TEXT("LaserSocket: Stopped listening"));
}

void ALaserSocketReceiver::OnDataReceived(const FArrayReaderPtr& Data, const FIPv4Endpoint& Endpoint)
{
    // Bu fonksiyon farklı thread'de çalışır!
    // Game thread'e güvenli şekilde aktarmalıyız
    
    FString Message;
    
    // Binary data'yı string'e çevir
    TArray<uint8> ReceivedData;
    ReceivedData.AddUninitialized(Data->TotalSize());
    Data->Serialize(ReceivedData.GetData(), Data->TotalSize());
    
    Message = FString(UTF8_TO_TCHAR(reinterpret_cast<const char*>(ReceivedData.GetData())));
    
    // Thread-safe kuyruğa ekle
    MessageQueue.Enqueue(Message);
}

void ALaserSocketReceiver::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // Game thread'de mesajları işle
    FString Message;
    while (MessageQueue.Dequeue(Message))
    {
        ProcessMessage(Message);
    }
}

void ALaserSocketReceiver::ProcessMessage(const FString& Message)
{
    // JSON parse
    TSharedPtr<FJsonObject> JsonObject;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Message);

    if (!FJsonSerializer::Deserialize(Reader, JsonObject) || !JsonObject.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("LaserSocket: Invalid JSON: %s"), *Message);
        return;
    }

    // Değerleri oku
    FString Type = JsonObject->GetStringField(TEXT("type"));
    
    if (Type == TEXT("laser_hit"))
    {
        float X = JsonObject->GetNumberField(TEXT("x"));
        float Y = JsonObject->GetNumberField(TEXT("y"));
        float Confidence = JsonObject->GetNumberField(TEXT("confidence"));

        // Blueprint event'i tetikle
        OnLaserHitReceived.Broadcast(X, Y, Confidence);
        
        UE_LOG(LogTemp, Log, TEXT("LaserHit: X=%.3f, Y=%.3f, Conf=%.2f"), X, Y, Confidence);
    }
}
```

---

## 2️⃣ CoordinateTransformer - Koordinat Dönüşümü

### Header Dosyası

```cpp
// CoordinateTransformer.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CoordinateTransformer.generated.h"

UCLASS(BlueprintType)
class UNREALPROJECT1_API UCoordinateTransformer : public UObject
{
    GENERATED_BODY()

public:
    /**
     * Normalize ekran koordinatlarını dünya koordinatlarına çevirir.
     * 
     * @param PlayerController - Kamera bilgisi için oyuncu controller
     * @param ScreenX - 0.0 - 1.0 arası yatay pozisyon
     * @param ScreenY - 0.0 - 1.0 arası dikey pozisyon
     * @param WorldLocation - Çıktı: Ray başlangıç noktası
     * @param WorldDirection - Çıktı: Ray yönü
     * @return Dönüşüm başarılı mı
     */
    UFUNCTION(BlueprintCallable, Category = "Laser|Coordinate")
    static bool ScreenToWorld(
        APlayerController* PlayerController,
        float ScreenX,
        float ScreenY,
        FVector& WorldLocation,
        FVector& WorldDirection
    );

    /**
     * Belirli bir kameradan ekran koordinatlarını dünya koordinatlarına çevirir.
     */
    UFUNCTION(BlueprintCallable, Category = "Laser|Coordinate")
    static bool CameraScreenToWorld(
        UCameraComponent* CameraComponent,
        float ScreenX,
        float ScreenY,
        FVector& WorldLocation,
        FVector& WorldDirection
    );
};
```

### Source Dosyası

```cpp
// CoordinateTransformer.cpp
#include "CoordinateTransformer.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/LocalPlayer.h"
#include "Kismet/GameplayStatics.h"

bool UCoordinateTransformer::ScreenToWorld(
    APlayerController* PlayerController,
    float ScreenX,
    float ScreenY,
    FVector& WorldLocation,
    FVector& WorldDirection)
{
    if (!PlayerController)
    {
        UE_LOG(LogTemp, Warning, TEXT("CoordinateTransformer: PlayerController is null"));
        return false;
    }

    // Viewport boyutlarını al
    int32 ViewportSizeX, ViewportSizeY;
    PlayerController->GetViewportSize(ViewportSizeX, ViewportSizeY);

    // Normalize koordinatları pixel koordinatlarına çevir
    FVector2D ScreenPosition(ScreenX * ViewportSizeX, ScreenY * ViewportSizeY);

    // Screen to World dönüşümü
    return PlayerController->DeprojectScreenPositionToWorld(
        ScreenPosition.X,
        ScreenPosition.Y,
        WorldLocation,
        WorldDirection
    );
}

bool UCoordinateTransformer::CameraScreenToWorld(
    UCameraComponent* CameraComponent,
    float ScreenX,
    float ScreenY,
    FVector& WorldLocation,
    FVector& WorldDirection)
{
    if (!CameraComponent)
    {
        UE_LOG(LogTemp, Warning, TEXT("CoordinateTransformer: CameraComponent is null"));
        return false;
    }

    // Kamera transform
    FTransform CameraTransform = CameraComponent->GetComponentTransform();
    
    // FOV ve aspect ratio
    float FOV = CameraComponent->FieldOfView;
    float AspectRatio = CameraComponent->AspectRatio;
    
    // Normalize koordinatları -1 ile 1 arasına çevir
    float NormX = (ScreenX - 0.5f) * 2.0f;
    float NormY = (ScreenY - 0.5f) * 2.0f;
    
    // FOV'a göre açı hesapla
    float HalfFOVRad = FMath::DegreesToRadians(FOV * 0.5f);
    float TanHalfFOV = FMath::Tan(HalfFOVRad);
    
    // Lokal yön vektörü
    FVector LocalDirection;
    LocalDirection.X = 1.0f; // İleri
    LocalDirection.Y = NormX * TanHalfFOV * AspectRatio; // Sağ/Sol
    LocalDirection.Z = -NormY * TanHalfFOV; // Yukarı/Aşağı (Y ters)
    LocalDirection.Normalize();
    
    // Dünya koordinatlarına dönüştür
    WorldLocation = CameraTransform.GetLocation();
    WorldDirection = CameraTransform.TransformVectorNoScale(LocalDirection);
    
    return true;
}
```

---

## 3️⃣ LaserTraceActor - Line Trace Sistemi

### Header Dosyası

```cpp
// LaserTraceActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LaserTraceActor.generated.h"

// Hit olayı için delegate
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnLaserTraceHit, FHitResult, HitResult, FName, HitBoneName);

UCLASS()
class UNREALPROJECT1_API ALaserTraceActor : public AActor
{
    GENERATED_BODY()

public:
    ALaserTraceActor();

    // Blueprint event - vuruş olduğunda
    UPROPERTY(BlueprintAssignable, Category = "Laser")
    FOnLaserTraceHit OnLaserTraceHit;

    // Trace ayarları
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Laser|Trace")
    float TraceDistance = 10000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Laser|Trace")
    TEnumAsByte<ECollisionChannel> TraceChannel = ECC_Visibility;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Laser|Debug")
    bool bDrawDebugLine = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Laser|Debug")
    float DebugLineDuration = 0.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Laser|Debug")
    FColor DebugLineColor = FColor::Red;

    /**
     * Belirtilen konum ve yönden line trace gerçekleştirir.
     */
    UFUNCTION(BlueprintCallable, Category = "Laser")
    bool PerformTrace(const FVector& StartLocation, const FVector& Direction, FHitResult& OutHitResult);

    /**
     * Normalize ekran koordinatlarından trace gerçekleştirir.
     * Koordinat dönüşümü dahili olarak yapılır.
     */
    UFUNCTION(BlueprintCallable, Category = "Laser")
    bool PerformTraceFromScreen(
        APlayerController* PlayerController,
        float ScreenX,
        float ScreenY,
        FHitResult& OutHitResult
    );

protected:
    // Vuruş noktasından bone ismini çıkar
    FName GetHitBoneName(const FHitResult& HitResult);
};
```

### Source Dosyası

```cpp
// LaserTraceActor.cpp
#include "LaserTraceActor.h"
#include "CoordinateTransformer.h"
#include "DrawDebugHelpers.h"
#include "Components/SkeletalMeshComponent.h"

ALaserTraceActor::ALaserTraceActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

bool ALaserTraceActor::PerformTrace(const FVector& StartLocation, const FVector& Direction, FHitResult& OutHitResult)
{
    FVector EndLocation = StartLocation + (Direction * TraceDistance);

    // Collision query parametreleri
    FCollisionQueryParams QueryParams;
    QueryParams.AddIgnoredActor(this);
    QueryParams.bTraceComplex = true;
    QueryParams.bReturnPhysicalMaterial = true;

    // Line trace
    bool bHit = GetWorld()->LineTraceSingleByChannel(
        OutHitResult,
        StartLocation,
        EndLocation,
        TraceChannel,
        QueryParams
    );

    // Debug çizim
    if (bDrawDebugLine)
    {
        FColor LineColor = bHit ? FColor::Green : DebugLineColor;
        FVector DrawEnd = bHit ? OutHitResult.ImpactPoint : EndLocation;
        
        DrawDebugLine(
            GetWorld(),
            StartLocation,
            DrawEnd,
            LineColor,
            false,
            DebugLineDuration,
            0,
            2.0f
        );

        if (bHit)
        {
            DrawDebugSphere(
                GetWorld(),
                OutHitResult.ImpactPoint,
                10.0f,
                12,
                FColor::Yellow,
                false,
                DebugLineDuration
            );
        }
    }

    // Vuruş olduysa event tetikle
    if (bHit)
    {
        FName BoneName = GetHitBoneName(OutHitResult);
        OnLaserTraceHit.Broadcast(OutHitResult, BoneName);
    }

    return bHit;
}

bool ALaserTraceActor::PerformTraceFromScreen(
    APlayerController* PlayerController,
    float ScreenX,
    float ScreenY,
    FHitResult& OutHitResult)
{
    FVector WorldLocation, WorldDirection;
    
    if (!UCoordinateTransformer::ScreenToWorld(
        PlayerController,
        ScreenX,
        ScreenY,
        WorldLocation,
        WorldDirection))
    {
        return false;
    }

    return PerformTrace(WorldLocation, WorldDirection, OutHitResult);
}

FName ALaserTraceActor::GetHitBoneName(const FHitResult& HitResult)
{
    // Skeletal mesh component ise bone ismini al
    if (USkeletalMeshComponent* SkelMesh = Cast<USkeletalMeshComponent>(HitResult.GetComponent()))
    {
        return HitResult.BoneName;
    }
    
    return NAME_None;
}
```

---

## 4️⃣ HitReactionComponent - Vuruş Tepki Sistemi

### Header Dosyası

```cpp
// HitReactionComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "HitReactionComponent.generated.h"

// Vuruş bölgesi enum
UENUM(BlueprintType)
enum class EHitZone : uint8
{
    None        UMETA(DisplayName = "None"),
    Head        UMETA(DisplayName = "Head"),
    Torso       UMETA(DisplayName = "Torso"),
    LeftArm     UMETA(DisplayName = "Left Arm"),
    RightArm    UMETA(DisplayName = "Right Arm"),
    LeftLeg     UMETA(DisplayName = "Left Leg"),
    RightLeg    UMETA(DisplayName = "Right Leg")
};

// Tepki tipi enum
UENUM(BlueprintType)
enum class EReactionType : uint8
{
    None        UMETA(DisplayName = "None"),
    Stun        UMETA(DisplayName = "Stun"),
    Knockback   UMETA(DisplayName = "Knockback"),
    Flinch      UMETA(DisplayName = "Flinch"),
    Stumble     UMETA(DisplayName = "Stumble"),
    Ragdoll     UMETA(DisplayName = "Ragdoll")
};

// Blueprint event delegate
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(
    FOnHitReaction,
    EHitZone, HitZone,
    EReactionType, ReactionType,
    FVector, HitDirection
);

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UNREALPROJECT1_API UHitReactionComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UHitReactionComponent();

    // Blueprint event
    UPROPERTY(BlueprintAssignable, Category = "HitReaction")
    FOnHitReaction OnHitReaction;

    // Bone → Zone mapping (Blueprint'ten düzenlenebilir)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "HitReaction|Mapping")
    TMap<FName, EHitZone> BoneToZoneMap;

    // Zone → Reaction mapping
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "HitReaction|Mapping")
    TMap<EHitZone, EReactionType> ZoneToReactionMap;

    /**
     * Hit result'tan bölge tespit eder ve tepki tetikler.
     */
    UFUNCTION(BlueprintCallable, Category = "HitReaction")
    void ProcessHit(const FHitResult& HitResult, FVector HitDirection);

    /**
     * Bone isminden zone tespit eder.
     */
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "HitReaction")
    EHitZone GetZoneFromBone(FName BoneName) const;

    /**
     * Zone'dan tepki tipi tespit eder.
     */
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "HitReaction")
    EReactionType GetReactionFromZone(EHitZone Zone) const;

protected:
    virtual void BeginPlay() override;
    
    // Varsayılan mapping'leri oluştur
    void InitializeDefaultMappings();
};
```

### Source Dosyası

```cpp
// HitReactionComponent.cpp
#include "HitReactionComponent.h"

UHitReactionComponent::UHitReactionComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UHitReactionComponent::BeginPlay()
{
    Super::BeginPlay();
    InitializeDefaultMappings();
}

void UHitReactionComponent::InitializeDefaultMappings()
{
    // Bone → Zone mapping (UE5 Mannequin için)
    if (BoneToZoneMap.Num() == 0)
    {
        // Head
        BoneToZoneMap.Add(TEXT("head"), EHitZone::Head);
        BoneToZoneMap.Add(TEXT("neck_01"), EHitZone::Head);
        BoneToZoneMap.Add(TEXT("neck_02"), EHitZone::Head);

        // Torso
        BoneToZoneMap.Add(TEXT("spine_01"), EHitZone::Torso);
        BoneToZoneMap.Add(TEXT("spine_02"), EHitZone::Torso);
        BoneToZoneMap.Add(TEXT("spine_03"), EHitZone::Torso);
        BoneToZoneMap.Add(TEXT("spine_04"), EHitZone::Torso);
        BoneToZoneMap.Add(TEXT("spine_05"), EHitZone::Torso);
        BoneToZoneMap.Add(TEXT("pelvis"), EHitZone::Torso);

        // Left Arm
        BoneToZoneMap.Add(TEXT("clavicle_l"), EHitZone::LeftArm);
        BoneToZoneMap.Add(TEXT("upperarm_l"), EHitZone::LeftArm);
        BoneToZoneMap.Add(TEXT("lowerarm_l"), EHitZone::LeftArm);
        BoneToZoneMap.Add(TEXT("hand_l"), EHitZone::LeftArm);

        // Right Arm
        BoneToZoneMap.Add(TEXT("clavicle_r"), EHitZone::RightArm);
        BoneToZoneMap.Add(TEXT("upperarm_r"), EHitZone::RightArm);
        BoneToZoneMap.Add(TEXT("lowerarm_r"), EHitZone::RightArm);
        BoneToZoneMap.Add(TEXT("hand_r"), EHitZone::RightArm);

        // Left Leg
        BoneToZoneMap.Add(TEXT("thigh_l"), EHitZone::LeftLeg);
        BoneToZoneMap.Add(TEXT("calf_l"), EHitZone::LeftLeg);
        BoneToZoneMap.Add(TEXT("foot_l"), EHitZone::LeftLeg);

        // Right Leg
        BoneToZoneMap.Add(TEXT("thigh_r"), EHitZone::RightLeg);
        BoneToZoneMap.Add(TEXT("calf_r"), EHitZone::RightLeg);
        BoneToZoneMap.Add(TEXT("foot_r"), EHitZone::RightLeg);
    }

    // Zone → Reaction mapping
    if (ZoneToReactionMap.Num() == 0)
    {
        ZoneToReactionMap.Add(EHitZone::Head, EReactionType::Stun);
        ZoneToReactionMap.Add(EHitZone::Torso, EReactionType::Knockback);
        ZoneToReactionMap.Add(EHitZone::LeftArm, EReactionType::Flinch);
        ZoneToReactionMap.Add(EHitZone::RightArm, EReactionType::Flinch);
        ZoneToReactionMap.Add(EHitZone::LeftLeg, EReactionType::Stumble);
        ZoneToReactionMap.Add(EHitZone::RightLeg, EReactionType::Stumble);
    }
}

void UHitReactionComponent::ProcessHit(const FHitResult& HitResult, FVector HitDirection)
{
    EHitZone Zone = GetZoneFromBone(HitResult.BoneName);
    EReactionType Reaction = GetReactionFromZone(Zone);

    UE_LOG(LogTemp, Log, TEXT("HitReaction: Bone=%s, Zone=%d, Reaction=%d"),
        *HitResult.BoneName.ToString(),
        static_cast<int32>(Zone),
        static_cast<int32>(Reaction));

    // Blueprint event tetikle
    OnHitReaction.Broadcast(Zone, Reaction, HitDirection);
}

EHitZone UHitReactionComponent::GetZoneFromBone(FName BoneName) const
{
    if (const EHitZone* Zone = BoneToZoneMap.Find(BoneName))
    {
        return *Zone;
    }
    return EHitZone::None;
}

EReactionType UHitReactionComponent::GetReactionFromZone(EHitZone Zone) const
{
    if (const EReactionType* Reaction = ZoneToReactionMap.Find(Zone))
    {
        return *Reaction;
    }
    return EReactionType::None;
}
```

---

## 5️⃣ Sistem Entegrasyonu - GameMode

### LaserGameMode.h

```cpp
// LaserGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "LaserGameMode.generated.h"

class ALaserSocketReceiver;
class ALaserTraceActor;

UCLASS()
class UNREALPROJECT1_API ALaserGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ALaserGameMode();
    virtual void BeginPlay() override;

    // Aktör referansları
    UPROPERTY(BlueprintReadOnly, Category = "Laser")
    ALaserSocketReceiver* SocketReceiver;

    UPROPERTY(BlueprintReadOnly, Category = "Laser")
    ALaserTraceActor* TraceActor;

protected:
    // Socket'ten lazer koordinatı alındığında
    UFUNCTION()
    void OnLaserHitReceived(float X, float Y, float Confidence);
};
```

### LaserGameMode.cpp

```cpp
// LaserGameMode.cpp
#include "LaserGameMode.h"
#include "LaserSocketReceiver.h"
#include "LaserTraceActor.h"
#include "Kismet/GameplayStatics.h"

ALaserGameMode::ALaserGameMode()
{
    // Default pawn ve controller ayarları
}

void ALaserGameMode::BeginPlay()
{
    Super::BeginPlay();

    // Socket receiver spawn
    FActorSpawnParameters SpawnParams;
    SocketReceiver = GetWorld()->SpawnActor<ALaserSocketReceiver>(
        ALaserSocketReceiver::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParams
    );

    // Trace actor spawn
    TraceActor = GetWorld()->SpawnActor<ALaserTraceActor>(
        ALaserTraceActor::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParams
    );

    // Event bağlantısı
    if (SocketReceiver)
    {
        SocketReceiver->OnLaserHitReceived.AddDynamic(this, &ALaserGameMode::OnLaserHitReceived);
        UE_LOG(LogTemp, Log, TEXT("LaserGameMode: Socket receiver initialized"));
    }
}

void ALaserGameMode::OnLaserHitReceived(float X, float Y, float Confidence)
{
    if (!TraceActor) return;

    // PlayerController al
    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    if (!PC) return;

    // Trace gerçekleştir
    FHitResult HitResult;
    if (TraceActor->PerformTraceFromScreen(PC, X, Y, HitResult))
    {
        UE_LOG(LogTemp, Log, TEXT("LaserHit: Actor=%s, Location=%s"),
            *HitResult.GetActor()->GetName(),
            *HitResult.ImpactPoint.ToString());
    }
}
```

---

## 📝 Derleme Notları

### Visual Studio Ayarları
1. Unreal Engine 5.7 için Visual Studio 2022 gerekli
2. "Game Development with C++" workload yüklü olmalı
3. Windows SDK 10.0.19041.0 veya üzeri

### Build Komutları
```powershell
# Proje regenerate
"C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\GenerateProjectFiles.bat" "path\to\unrealproject1.uproject" -game

# Build
"C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" unrealproject1 Win64 Development "path\to\unrealproject1.uproject"
```

---

*Son Güncelleme: 10 Ocak 2026*

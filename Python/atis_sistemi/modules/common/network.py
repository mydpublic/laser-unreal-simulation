"""
Lazer Atış Sistemi - Network İletişim Modülü

Bu modül, Python uygulamasından Unreal Engine'a gerçek zamanlı
lazer koordinat verisi göndermek için socket iletişim sağlar.

Desteklenen Protokoller:
- UDP: Düşük gecikme, kayıp toleransı olan durumlar için
- TCP: Güvenilir iletişim gereken durumlar için

Kullanım:
    client = LaserSocketClient(host="127.0.0.1", port=7777, protocol="UDP")
    client.connect()
    client.send_hit_event(x=0.5, y=0.3, confidence=0.95)
    client.disconnect()
"""

import socket
import json
import time
import threading
from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Protocol(Enum):
    """Desteklenen iletişim protokolleri"""
    UDP = "UDP"
    TCP = "TCP"


@dataclass
class LaserHitMessage:
    """Lazer vuruş mesajı veri yapısı"""
    type: str = "laser_hit"
    x: float = 0.0
    y: float = 0.0
    timestamp: float = 0.0
    confidence: float = 1.0
    
    def to_json(self) -> str:
        """Mesajı JSON string'e çevirir"""
        return json.dumps(asdict(self))
    
    def to_bytes(self) -> bytes:
        """Mesajı byte dizisine çevirir (socket gönderimi için)"""
        return self.to_json().encode('utf-8')


@dataclass
class HeartbeatMessage:
    """Bağlantı kontrolü için heartbeat mesajı"""
    type: str = "heartbeat"
    timestamp: float = 0.0
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
    def to_bytes(self) -> bytes:
        return self.to_json().encode('utf-8')


class LaserSocketClient:
    """
    Unreal Engine'a lazer koordinat verisi gönderen socket client.
    
    UDP ve TCP protokollerini destekler. UDP düşük gecikme için önerilir.
    
    Attributes:
        host: Hedef IP adresi (varsayılan: 127.0.0.1)
        port: Hedef port numarası (varsayılan: 7777)
        protocol: İletişim protokolü (UDP veya TCP)
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 7777, 
                 protocol: str = "UDP", auto_reconnect: bool = True):
        """
        LaserSocketClient constructor.
        
        Args:
            host: Unreal Engine'ın çalıştığı IP adresi
            port: Dinleme portu (Unreal tarafında açık olmalı)
            protocol: "UDP" veya "TCP"
            auto_reconnect: Bağlantı koptuğunda otomatik yeniden bağlan
        """
        self.host = host
        self.port = port
        self.protocol = Protocol(protocol.upper())
        self.auto_reconnect = auto_reconnect
        
        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._lock = threading.Lock()
        
        # İstatistikler
        self._messages_sent = 0
        self._last_send_time = 0.0
        self._errors = 0
    
    @property
    def is_connected(self) -> bool:
        """Bağlantı durumunu döndürür"""
        return self._connected
    
    @property
    def stats(self) -> dict:
        """İletişim istatistiklerini döndürür"""
        return {
            "messages_sent": self._messages_sent,
            "last_send_time": self._last_send_time,
            "errors": self._errors,
            "connected": self._connected
        }
    
    def connect(self) -> bool:
        """
        Socket bağlantısını başlatır.
        
        Returns:
            Bağlantı başarılı ise True
        """
        with self._lock:
            try:
                if self.protocol == Protocol.UDP:
                    self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    # UDP için connect opsiyonel ama hedef adresi sabitler
                    self._socket.connect((self.host, self.port))
                else:  # TCP
                    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self._socket.settimeout(5.0)  # 5 saniye timeout
                    self._socket.connect((self.host, self.port))
                
                self._connected = True
                self._errors = 0
                print(f"[Network] Connected to {self.host}:{self.port} via {self.protocol.value}")
                return True
                
            except socket.error as e:
                self._connected = False
                self._errors += 1
                print(f"[Network] Connection failed: {e}")
                return False
    
    def disconnect(self) -> None:
        """Socket bağlantısını kapatır"""
        with self._lock:
            if self._socket:
                try:
                    self._socket.close()
                except:
                    pass
                self._socket = None
            self._connected = False
            print("[Network] Disconnected")
    
    def _send_data(self, data: bytes) -> bool:
        """
        Ham veri gönderir (internal).
        
        Args:
            data: Gönderilecek byte dizisi
            
        Returns:
            Gönderim başarılı ise True
        """
        if not self._connected or not self._socket:
            if self.auto_reconnect:
                self.connect()
            if not self._connected:
                return False
        
        try:
            with self._lock:
                if self.protocol == Protocol.UDP:
                    self._socket.send(data)
                else:  # TCP
                    self._socket.sendall(data)
                
                self._messages_sent += 1
                self._last_send_time = time.time()
                return True
                
        except socket.error as e:
            self._errors += 1
            self._connected = False
            print(f"[Network] Send error: {e}")
            
            if self.auto_reconnect:
                self.connect()
            return False
    
    def send_coordinates(self, x: float, y: float, timestamp: float = None) -> bool:
        """
        Normalize edilmiş koordinatları gönderir.
        
        Args:
            x: 0.0 - 1.0 arası yatay pozisyon (sol=0, sağ=1)
            y: 0.0 - 1.0 arası dikey pozisyon (üst=0, alt=1)
            timestamp: Unix timestamp (None ise otomatik)
            
        Returns:
            Gönderim başarılı ise True
        """
        if timestamp is None:
            timestamp = time.time()
        
        message = LaserHitMessage(
            type="laser_position",
            x=float(x),
            y=float(y),
            timestamp=timestamp,
            confidence=1.0
        )
        
        return self._send_data(message.to_bytes())
    
    def send_hit_event(self, x: float, y: float, confidence: float = 1.0, 
                       timestamp: float = None) -> bool:
        """
        Tespit edilen atış olayını gönderir.
        
        Bu metod lazer atışı tespit edildiğinde çağrılır.
        Unreal Engine bu mesajı alarak Line Trace başlatır.
        
        Args:
            x: 0.0 - 1.0 arası yatay pozisyon
            y: 0.0 - 1.0 arası dikey pozisyon
            confidence: Tespit güvenilirliği (0.0 - 1.0)
            timestamp: Unix timestamp (None ise otomatik)
            
        Returns:
            Gönderim başarılı ise True
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Koordinatları 0-1 aralığına sınırla
        x = max(0.0, min(1.0, float(x)))
        y = max(0.0, min(1.0, float(y)))
        confidence = max(0.0, min(1.0, float(confidence)))
        
        message = LaserHitMessage(
            type="laser_hit",
            x=x,
            y=y,
            timestamp=timestamp,
            confidence=confidence
        )
        
        return self._send_data(message.to_bytes())
    
    def send_heartbeat(self) -> bool:
        """
        Bağlantı kontrolü için heartbeat gönderir.
        
        Returns:
            Gönderim başarılı ise True
        """
        message = HeartbeatMessage(
            timestamp=time.time()
        )
        return self._send_data(message.to_bytes())
    
    def __enter__(self):
        """Context manager desteği - with statement için"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager çıkışı"""
        self.disconnect()
        return False


class NetworkManager:
    """
    Ağ bağlantısını yöneten üst seviye sınıf.
    
    Heartbeat, reconnect ve thread-safe operasyonları yönetir.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 7777,
                 protocol: str = "UDP", heartbeat_interval: float = 5.0):
        """
        NetworkManager constructor.
        
        Args:
            host: Hedef IP adresi
            port: Hedef port
            protocol: UDP veya TCP
            heartbeat_interval: Heartbeat gönderim aralığı (saniye)
        """
        self.client = LaserSocketClient(host, port, protocol)
        self.heartbeat_interval = heartbeat_interval
        
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._running = False
    
    def start(self) -> bool:
        """
        Network manager'ı başlatır ve heartbeat thread'i çalıştırır.
        
        Returns:
            Başlatma başarılı ise True
        """
        if not self.client.connect():
            return False
        
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        
        return True
    
    def stop(self) -> None:
        """Network manager'ı durdurur"""
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2.0)
        self.client.disconnect()
    
    def _heartbeat_loop(self) -> None:
        """Periyodik heartbeat gönderen thread fonksiyonu"""
        while self._running:
            self.client.send_heartbeat()
            time.sleep(self.heartbeat_interval)
    
    def send_hit(self, x: float, y: float, confidence: float = 1.0) -> bool:
        """
        Lazer vuruş olayı gönderir.
        
        Args:
            x, y: Normalize koordinatlar (0-1)
            confidence: Tespit güvenilirliği
            
        Returns:
            Gönderim başarılı ise True
        """
        return self.client.send_hit_event(x, y, confidence)
    
    @property
    def is_connected(self) -> bool:
        return self.client.is_connected
    
    @property
    def stats(self) -> dict:
        return self.client.stats


# Test kodu - doğrudan çalıştırıldığında
if __name__ == "__main__":
    print("=== LaserSocketClient Test ===\n")
    
    # Test 1: Basit bağlantı testi
    print("Test 1: UDP Client oluşturma...")
    client = LaserSocketClient(host="127.0.0.1", port=7777, protocol="UDP")
    print(f"  Protocol: {client.protocol.value}")
    print(f"  Target: {client.host}:{client.port}")
    
    # Test 2: Mesaj oluşturma
    print("\nTest 2: Mesaj oluşturma...")
    msg = LaserHitMessage(x=0.5, y=0.3, confidence=0.95, timestamp=time.time())
    print(f"  JSON: {msg.to_json()}")
    
    # Test 3: Bağlantı denemesi (Unreal çalışmıyorsa başarısız olacak)
    print("\nTest 3: Bağlantı denemesi...")
    if client.connect():
        print("  ✅ Bağlantı başarılı!")
        
        # Test mesaj gönder
        print("\nTest 4: Mesaj gönderimi...")
        for i in range(3):
            success = client.send_hit_event(x=0.5 + i*0.1, y=0.5, confidence=0.9)
            print(f"  Mesaj {i+1}: {'✅' if success else '❌'}")
            time.sleep(0.1)
        
        print(f"\n  İstatistikler: {client.stats}")
        client.disconnect()
    else:
        print("  ⚠️ Bağlantı başarısız (Unreal Engine çalışmıyor olabilir)")
        print("  Bu normal - Unreal tarafı hazır olduğunda test edilebilir")
    
    print("\n=== Test Tamamlandı ===")

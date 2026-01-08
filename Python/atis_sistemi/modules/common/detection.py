# OpenCV kütüphanesi - görüntü işleme için
import cv2
# NumPy kütüphanesi - sayısal işlemler için
import numpy as np

# Tespit parametrelerini içeren sabitler sınıfı
from modules.common.constants import DetectionConstants


class Detection:
    """
    Lazer atış tespiti için görüntü işleme sınıfı.
    Frame difference ve renk tespiti yöntemleriyle kırmızı lazer noktalarını algılar.
    """
    
    def __init__(self):
        # Önceki frame'in bulanık görüntüsünü saklar (hareket tespiti için)
        self.__blurred_previous_image = None

    @staticmethod
    def __is_red(image):
        """
        Verilen görüntü bölgesinin kırmızı renk içerip içermediğini kontrol eder.
        
        Args:
            image: BGR formatında görüntü bölgesi
            
        Returns:
            Kırmızı piksel sayısı (0 ise kırmızı değil)
        """
        # BGR'den HSV renk uzayına dönüştür (renk tespiti için daha uygun)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Sol kırmızı maske (0-10 derece arası Hue değerleri)
        mask_left = cv2.inRange(hsv, DetectionConstants.LOWER_LEFT_RED, DetectionConstants.UPPER_LEFT_RED)
        
        # Sağ kırmızı maske (160-180 derece arası Hue değerleri)
        # Not: HSV'de kırmızı renk 0 ve 180 derecede bulunur
        mask_right = cv2.inRange(hsv, DetectionConstants.LOWER_RIGHT_RED, DetectionConstants.UPPER_RIGHT_RED)
        
        # İki maskeyi birleştir ve kırmızı piksel sayısını döndür
        return np.count_nonzero((mask_left | mask_right))

    def detect(self, image):
        """
        Gelen frame'de lazer atış noktalarını tespit eder.
        
        Algoritma:
        1. Gaussian blur ile gürültü azaltma
        2. Önceki frame ile fark alma (hareket tespiti)
        3. Adaptive thresholding (otomatik eşikleme)
        4. Contour detection (şekil tespiti)
        5. Kırmızı renk doğrulama
        6. Merkez nokta hesaplama
        
        Args:
            image: BGR formatında giriş görüntüsü
            
        Returns:
            Tespit edilen lazer noktalarının merkez koordinatları [(x, y), ...]
        """
        # Gaussian blur uygula (5x5 kernel ile gürültü azaltma)
        blurred_image = cv2.GaussianBlur(image, DetectionConstants.KERNEL_SIZE, DetectionConstants.SIGMA_X)

        try:
            # Önceki ve şimdiki frame arasındaki farkı al (sadece kırmızı kanal [:, :, 2])
            # Bu sayede hareketi/atışı yakalayabiliriz
            diff_red = cv2.absdiff(blurred_image, self.__blurred_previous_image)[:, :, 2]
            
            # OTSU algoritması ile otomatik eşik değeri hesapla
            # Bu algoritma görüntü histogramına göre optimal eşik bulur
            adaptive, _ = cv2.threshold(diff_red,
                                        DetectionConstants.MIN_VALUE,
                                        DetectionConstants.MAX_VALUE,
                                        cv2.THRESH_OTSU)
            
            # Binary threshold uygula (adaptive ve MIN_ADAPTIVE'den büyük olanı kullan)
            # Eşik değerinden büyük pikseller 255, küçükler 0 olur
            _, mask_red = cv2.threshold(diff_red,
                                        max(adaptive, DetectionConstants.MIN_ADAPTIVE),
                                        DetectionConstants.MAX_VALUE,
                                        cv2.THRESH_BINARY)
            
            # Canny kenar algılama sonrası contour (şekil) bulma
            # RETR_EXTERNAL: Sadece dış konturları al
            # CHAIN_APPROX_SIMPLE: Contour noktalarını sıkıştır (gereksiz noktaları at)
            contours, _ = cv2.findContours(
                cv2.Canny(mask_red, DetectionConstants.CANNY_THRESHOLD1, DetectionConstants.CANNY_THRESHOLD2),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

            # Tespit edilen noktaları saklamak için liste
            points = list()
            
            # Her bir contour için işlem yap
            for contour in contours:
                # Minimum alan kontrolü (gürültü filtreleme - 10 pikselden küçükleri atla)
                if cv2.contourArea(contour) > DetectionConstants.MIN_CONTOUR_AREA:
                    # Contour etrafına dikdörtgen çiz ve koordinatlarını al
                    x, y, width, height = cv2.boundingRect(contour)

                    # Dikdörtgen içindeki bölgenin gerçekten kırmızı olup olmadığını kontrol et
                    # (Yanlış pozitif tespitleri engeller)
                    if self.__is_red(image[y:y + height, x:x + width]):
                        # Dikdörtgenin merkez noktasını hesapla ve listeye ekle
                        points.append((x + width // 2, (y + height // 2)))
            
            # Tespit edilen tüm noktaları döndür
            return points
            
        except cv2.error:
            # İlk frame'de veya hata durumunda boş liste döndür
            return list()
            
        finally:
            # Bir sonraki tespit için şimdiki frame'i sakla
            self.__blurred_previous_image = blurred_image

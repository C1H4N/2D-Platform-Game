# 2D Platform Oyunu

Pygame ile geliştirilmiş, üç seviyeli bir platform oyunu. Her seviyede artan zorluk seviyesi ve farklı harita tasarımları bulunmaktadır.

## Özellikler

### Oynanış
- Basit ve akıcı karakter kontrolü (koşma, zıplama)
- Platform üzerinde hareket
- Toplanabilir altınlar
- Hareketli düşmanlar
- Can sistemi
- Üç farklı seviye
- Seviye ilerledikçe artan zorluk

### Görsel Özellikler
- Animasyonlu karakter (koşma, zıplama)
- Dönen ve parlayan altınlar
- Parçacık efektleri (altın toplama, hasar alma)
- Paralaks arka plan (bulutlar ve dağlar)
- Modern arayüz tasarımı

### Ses Efektleri
- Zıplama sesi
- Altın toplama sesi
- Hasar alma sesi
- Ölüm sesi

## Kurulum

1. Python'u yükleyin (3.11 veya üstü önerilir)
2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Oyunu başlatın:
```bash
python main.py
```

## Kontroller
- **Sağ/Sol Ok Tuşları**: Hareket
- **Boşluk**: Zıplama
- **ESC**: Oyundan çıkış / Menüye dönüş

## Seviyeler

### Seviye 1 (Kolay)
- 3 platform
- 6 altın
- Yavaş düşmanlar
- 3 can

### Seviye 2 (Orta)
- 4 platform
- 8 altın
- Orta hızlı düşmanlar
- 2 can

### Seviye 3 (Zor)
- 7 platform
- 10 altın
- Hızlı düşmanlar
- 1 can

## Geliştirici

Bu proje, GitHub profilimi zenginleştirmek için oluşturulmuş örnek bir projedir. Pygame kütüphanesi kullanılarak geliştirilmiştir.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız. 
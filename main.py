import pygame
import sys
import random
import math
import os
import wave
import struct

# Pygame başlatma
pygame.init()
pygame.mixer.init()  # Ses sistemi başlatma

# FPS ayarı için clock
clock = pygame.time.Clock()

# Ekran ayarları
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platform Oyunu")

# Asset klasörü oluşturma
if not os.path.exists('assets'):
    os.makedirs('assets')
if not os.path.exists('assets/sounds'):
    os.makedirs('assets/sounds')

# Ses dosyalarını oluşturma
def create_wav(filename, frequency, duration):
    # WAV dosyası parametreleri
    sample_rate = 44100
    amplitude = 4096
    num_samples = int(sample_rate * duration)
    
    wav_file = wave.open(filename, 'w')
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 2 bytes per sample
    wav_file.setframerate(sample_rate)
    
    # Ses dalgası oluşturma
    for i in range(num_samples):
        sample = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
        packed_sample = struct.pack('h', int(sample))
        wav_file.writeframes(packed_sample)
    
    wav_file.close()

# Ses dosyaları
if not os.path.exists('assets/sounds/jump.wav'):
    create_wav('assets/sounds/jump.wav', 440, 0.1)  # Zıplama: orta ton, kısa
if not os.path.exists('assets/sounds/coin.wav'):
    create_wav('assets/sounds/coin.wav', 880, 0.07)  # Altın: yüksek ton, çok kısa
if not os.path.exists('assets/sounds/hit.wav'):
    create_wav('assets/sounds/hit.wav', 220, 0.2)  # Hasar: düşük ton, orta
if not os.path.exists('assets/sounds/death.wav'):
    create_wav('assets/sounds/death.wav', 110, 0.4)  # Ölüm: çok düşük ton, uzun

# Ses efektleri
jump_sound = pygame.mixer.Sound('assets/sounds/jump.wav')
coin_sound = pygame.mixer.Sound('assets/sounds/coin.wav')
hit_sound = pygame.mixer.Sound('assets/sounds/hit.wav')
death_sound = pygame.mixer.Sound('assets/sounds/death.wav')

# Ses ayarları
jump_sound.set_volume(0.3)
coin_sound.set_volume(0.4)
hit_sound.set_volume(0.5)
death_sound.set_volume(0.6)

# Renkler ve Sabitler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 215, 0)
PURPLE = (128, 0, 128)
SKY_BLUE = (135, 206, 235)

# Parçacık efekti sınıfı
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed_x, speed_y, size=3, lifetime=30):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.lifetime = lifetime
        self.alpha = 255
        self.fade_speed = 255 / lifetime

    def update(self):
        self.float_x += self.speed_x
        self.float_y += self.speed_y
        self.speed_y += 0.2  # Yerçekimi
        self.rect.x = self.float_x
        self.rect.y = self.float_y
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - self.fade_speed)
        self.image.set_alpha(self.alpha)

# Karakter sprite'ı güncelleme
def create_player_sprite(frame=0, jumping=False):
    surf = pygame.Surface((30, 50), pygame.SRCALPHA)
    
    # Bacak animasyonu
    if jumping:
        # Zıplama pozu
        pygame.draw.rect(surf, (50, 50, 255), (8, 40, 6, 8))
        pygame.draw.rect(surf, (50, 50, 255), (16, 40, 6, 8))
    else:
        # Koşma animasyonu
        leg_offset = math.sin(frame * 0.5) * 5
        pygame.draw.rect(surf, (50, 50, 255), (8, 40 + leg_offset, 6, 10))
        pygame.draw.rect(surf, (50, 50, 255), (16, 40 - leg_offset, 6, 10))
    
    # Vücut
    pygame.draw.rect(surf, (255, 100, 100), (5, 10, 20, 30))
    
    # Kafa
    pygame.draw.circle(surf, (255, 200, 150), (15, 10), 8)
    
    # Gözler
    pygame.draw.circle(surf, BLACK, (12, 8), 2)
    pygame.draw.circle(surf, BLACK, (18, 8), 2)
    
    return surf

# Platform sprite'ı
def create_platform_sprite(width, height):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    # Ana platform
    pygame.draw.rect(surf, (34, 139, 34), (0, 0, width, height))
    # Çim efekti
    for i in range(0, width, 5):
        pygame.draw.line(surf, (50, 205, 50), (i, 0), (i, 3), 2)
    return surf

# Altın sprite'ı
def create_coin_sprite():
    surf = pygame.Surface((15, 15), pygame.SRCALPHA)
    # Altın daire
    pygame.draw.circle(surf, YELLOW, (7, 7), 7)
    # Parlaklık efekti
    pygame.draw.circle(surf, (255, 255, 200), (5, 5), 2)
    return surf

# Düşman sprite'ı
def create_enemy_sprite():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Vücut
    pygame.draw.rect(surf, PURPLE, (0, 0, 30, 30))
    # Gözler
    pygame.draw.circle(surf, RED, (10, 10), 3)
    pygame.draw.circle(surf, RED, (20, 10), 3)
    # Ağız
    pygame.draw.line(surf, RED, (8, 20), (22, 20), 2)
    return surf

# Arka plan
def create_background():
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Gökyüzü
    surf.fill(SKY_BLUE)
    # Bulutlar
    for _ in range(5):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT//2)
        pygame.draw.ellipse(surf, WHITE, (x, y, 60, 30))
    # Dağlar
    for i in range(3):
        points = [
            (SCREEN_WIDTH * i//3, SCREEN_HEIGHT),
            (SCREEN_WIDTH * (i + 0.5)//3, SCREEN_HEIGHT//2),
            (SCREEN_WIDTH * (i + 1)//3, SCREEN_HEIGHT)
        ]
        pygame.draw.polygon(surf, (100, 100, 100), points)
    return surf

background = create_background()

# Font ayarları
pygame.font.init()
title_font = pygame.font.SysFont('Arial', 64)
button_font = pygame.font.SysFont('Arial', 32)
score_font = pygame.font.SysFont('Arial', 36)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.hover_color = tuple(max(0, min(255, c + 30)) for c in color)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surface = button_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

def show_start_screen():
    start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "BAŞLAT", BLUE)
    quit_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, "ÇIKIŞ", RED)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if start_button.handle_event(event):
                return True
            if quit_button.handle_event(event):
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)
        
        # Başlık
        title_surface = title_font.render("2D Platform Oyunu", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        screen.blit(title_surface, title_rect)
        
        # Butonlar
        start_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def show_death_screen(score):
    retry_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "TEKRAR OYNA", BLUE)
    quit_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, "ÇIKIŞ", RED)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if retry_button.handle_event(event):
                return True
            if quit_button.handle_event(event):
                return False

        screen.fill(BLACK)
        
        # Oyun Bitti yazısı
        game_over_text = title_font.render("OYUN BİTTİ!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 - 50))
        screen.blit(game_over_text, game_over_rect)
        
        # Final skor
        score_text = score_font.render(f"Final Puanın: {score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 50))
        screen.blit(score_text, score_rect)
        
        # Butonlar
        retry_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

# Oyuncu sınıfı güncelleme
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_player_sprite()
        self.original_image = self.image
        self.facing_right = True
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 100
        self.velocity_y = 0
        self.jumping = False
        self.speed = 5
        self.score = 0
        self.health = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.knockback_speed = 10
        self.animation_frame = 0
        self.moving = False

    def update(self):
        # Yerçekimi
        self.velocity_y += 0.8
        self.rect.y += self.velocity_y

        # Ekran sınırları
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.jumping = False

        # Animasyon güncelleme
        keys = pygame.key.get_pressed()
        self.moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
        
        if self.moving and not self.jumping:
            self.animation_frame += 0.2
            self.image = create_player_sprite(self.animation_frame, self.jumping)
        elif self.jumping:
            self.image = create_player_sprite(0, True)
        else:
            self.image = create_player_sprite(0, False)

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # Hasar alınamaz süre kontrolü ve yanıp sönme efekti
        if self.invulnerable:
            self.invulnerable_timer += 1
            if self.invulnerable_timer % 4 < 2:  # Yanıp sönme efekti
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
            if self.invulnerable_timer > 60:
                self.invulnerable = False
                self.invulnerable_timer = 0
                self.image.set_alpha(255)

        # Karakter yönü
        if keys[pygame.K_RIGHT] and not self.facing_right:
            self.facing_right = True
        elif keys[pygame.K_LEFT] and self.facing_right:
            self.facing_right = False

    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True
            jump_sound.play()  # Zıplama sesi
        
    def take_damage(self, enemy_pos):
        if not self.invulnerable:
            self.health -= 1
            self.invulnerable = True
            self.image.fill(GRAY)
            
            if self.health <= 0:
                death_sound.play()  # Ölüm sesi
            else:
                hit_sound.play()  # Hasar alma sesi
            
            # Geri tepme
            if self.rect.centerx < enemy_pos[0]:
                self.rect.x -= self.knockback_speed
            else:
                self.rect.x += self.knockback_speed
            self.velocity_y = -5

# Platform sınıfı
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = create_platform_sprite(width, height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Altın sınıfı
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_coin_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.original_y = y
        self.float_offset = 0
        self.float_speed = 0.002
        self.float_range = 3
        self.rotation = 0
        self.scale = 1.0

    def update(self):
        # Süzülme ve dönme animasyonu
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * self.float_range
        self.rect.y = self.original_y + self.float_offset
        self.rotation += 2
        self.scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.1
        
        rotated = pygame.transform.rotozoom(create_coin_sprite(), self.rotation, self.scale)
        self.image = rotated
        new_rect = rotated.get_rect()
        new_rect.center = self.rect.center
        self.rect = new_rect

# Düşman sınıfı
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_width):
        super().__init__()
        self.image = create_enemy_sprite()
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.rect.height
        self.speed = 2
        self.direction = 1
        self.start_x = x
        self.platform_width = platform_width

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right > self.start_x + self.platform_width - 30:
            self.direction = -1
            self.image = pygame.transform.flip(self.original_image, True, False)
        elif self.rect.left < self.start_x:
            self.direction = 1
            self.image = self.original_image

# Seviye tasarımları
LEVELS = [
    {
        'platforms': [
            {'x': 0, 'y': SCREEN_HEIGHT - 50, 'width': SCREEN_WIDTH, 'height': 50},  # Zemin
            {'x': 300, 'y': 400, 'width': 200, 'height': 20},
            {'x': 100, 'y': 300, 'width': 200, 'height': 20},
            {'x': 500, 'y': 200, 'width': 200, 'height': 20},
        ],
        'coins': [
            (350, 350), (150, 250), (550, 150),
            (400, 350), (200, 250), (600, 150),
        ],
        'enemy_speed': 2,
        'player_health': 3
    },
    {
        'platforms': [
            {'x': 0, 'y': SCREEN_HEIGHT - 50, 'width': SCREEN_WIDTH, 'height': 50},
            {'x': 100, 'y': 450, 'width': 150, 'height': 20},
            {'x': 350, 'y': 350, 'width': 150, 'height': 20},
            {'x': 600, 'y': 250, 'width': 150, 'height': 20},
            {'x': 200, 'y': 200, 'width': 150, 'height': 20},
        ],
        'coins': [
            (150, 400), (400, 300), (650, 200),
            (250, 150), (500, 300), (300, 400),
            (450, 200), (700, 200)
        ],
        'enemy_speed': 3,
        'player_health': 2
    },
    {
        'platforms': [
            {'x': 0, 'y': SCREEN_HEIGHT - 50, 'width': SCREEN_WIDTH, 'height': 50},
            {'x': 50, 'y': 450, 'width': 100, 'height': 20},
            {'x': 250, 'y': 400, 'width': 100, 'height': 20},
            {'x': 450, 'y': 350, 'width': 100, 'height': 20},
            {'x': 650, 'y': 300, 'width': 100, 'height': 20},
            {'x': 450, 'y': 250, 'width': 100, 'height': 20},
            {'x': 250, 'y': 200, 'width': 100, 'height': 20},
            {'x': 50, 'y': 150, 'width': 100, 'height': 20},
        ],
        'coins': [
            (100, 400), (300, 350), (500, 300),
            (700, 250), (500, 200), (300, 150),
            (100, 100), (400, 200), (600, 350),
            (200, 300)
        ],
        'enemy_speed': 4,
        'player_health': 1
    }
]

def show_level_screen(level_number, total_score):
    continue_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50, "DEVAM ET", GREEN)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if continue_button.handle_event(event):
                return True

        screen.fill(BLACK)
        
        # Seviye başlığı
        level_text = title_font.render(f"SEVİYE {level_number + 1}", True, BLUE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        screen.blit(level_text, level_rect)
        
        # Toplam puan
        score_text = score_font.render(f"Toplam Puan: {total_score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(score_text, score_rect)
        
        # Seviye bilgisi
        info_text = score_font.render(f"Düşman Hızı: {LEVELS[level_number]['enemy_speed']}", True, WHITE)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(info_text, info_rect)
        
        health_text = score_font.render(f"Can: {LEVELS[level_number]['player_health']}", True, RED)
        health_rect = health_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
        screen.blit(health_text, health_rect)
        
        # Buton
        continue_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def game_loop(level_number=0, total_score=0):
    # Sprite grupları
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    particles = pygame.sprite.Group()

    # Seviye verilerini al
    level_data = LEVELS[level_number]

    # Oyuncu oluşturma
    player = Player()
    player.health = level_data['player_health']
    all_sprites.add(player)

    # Platformları oluşturma
    for platform_data in level_data['platforms']:
        platform = Platform(platform_data['x'], platform_data['y'], 
                          platform_data['width'], platform_data['height'])
        all_sprites.add(platform)
        platforms.add(platform)

    # Altınları oluşturma
    for coin_pos in level_data['coins']:
        coin = Coin(coin_pos[0], coin_pos[1])
        all_sprites.add(coin)
        coins.add(coin)

    # Düşmanları oluşturma (her platformda bir düşman)
    for platform in platforms:
        if platform.rect.y < SCREEN_HEIGHT - 60:  # Zemin hariç
            enemy = Enemy(platform.rect.x, platform.rect.y, platform.rect.width)
            enemy.speed = level_data['enemy_speed']
            all_sprites.add(enemy)
            enemies.add(enemy)

    running = True
    while running:
        # Event kontrolü
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_ESCAPE:
                    return True

        # Tuş kontrolü
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rect.x -= player.speed
        if keys[pygame.K_RIGHT]:
            player.rect.x += player.speed

        # Platform çarpışma kontrolü
        player.rect.y += 1
        hits = pygame.sprite.spritecollide(player, platforms, False)
        player.rect.y -= 1

        if hits and player.velocity_y >= 0:
            player.rect.bottom = hits[0].rect.top
            player.velocity_y = 0
            player.jumping = False

        # Altın toplama kontrolü
        coin_hits = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_hits:
            player.score += 10
            coin_sound.play()
            
            # Altın toplama efekti
            for _ in range(10):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 5)
                particle = Particle(
                    coin.rect.centerx,
                    coin.rect.centery,
                    YELLOW,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    size=2,
                    lifetime=20
                )
                all_sprites.add(particle)
                particles.add(particle)

            # Tüm altınlar toplandıysa seviye tamamlandı
            if len(coins) == 0:
                return {'status': 'completed', 'score': player.score}

        # Düşman çarpışma kontrolü
        enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
        if enemy_hits:
            player.take_damage(enemy_hits[0].rect.center)
            if player.health <= 0:
                # Ölüm efekti
                for _ in range(30):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(3, 8)
                    particle = Particle(
                        player.rect.centerx,
                        player.rect.centery,
                        RED,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        size=4,
                        lifetime=40
                    )
                    all_sprites.add(particle)
                    particles.add(particle)
                return {'status': 'dead', 'score': total_score + player.score}

        # Güncelleme
        all_sprites.update()
        
        # Ölen parçacıkları temizle
        for particle in particles.copy():
            if particle.lifetime <= 0:
                particle.kill()

        # Çizim
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        
        # Puan ve can göstergesi
        score_text = score_font.render(f'Seviye Puanı: {player.score}', True, WHITE)
        total_score_text = score_font.render(f'Toplam Puan: {total_score + player.score}', True, WHITE)
        level_text = score_font.render(f'Seviye: {level_number + 1}', True, WHITE)
        health_text = score_font.render(f'Can: {player.health}', True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(total_score_text, (10, 50))
        screen.blit(level_text, (10, 90))
        screen.blit(health_text, (10, 130))
        
        pygame.display.flip()

        # FPS ayarı
        clock.tick(60)

    return {'status': 'quit', 'score': total_score + player.score}

# Ana oyun döngüsü güncelleme
while True:
    if show_start_screen():
        current_level = 0
        total_score = 0
        
        while current_level < len(LEVELS):
            if not show_level_screen(current_level, total_score):
                break
                
            result = game_loop(current_level, total_score)
            
            if result['status'] == 'completed':
                total_score += result['score']
                current_level += 1
                if current_level >= len(LEVELS):
                    # Oyun başarıyla tamamlandı
                    if not show_death_screen(total_score):
                        break
            elif result['status'] == 'dead':
                if not show_death_screen(result['score']):
                    break
                break
            else:  # quit
                break
    else:
        break

pygame.quit()
sys.exit() 
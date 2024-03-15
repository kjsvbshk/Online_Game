import pygame
import random
import os
import threading
from DB_Connect import Send_Data, Reference

# Inicializar Pygame
pygame.init()   

# Definir colores
WHITE = (255, 255, 255)
BLACK = (0,0,0)

# Definir dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600

# Ruta de los recursos
assets = os.path.join(os.path.dirname(__file__), 'Recursos')

# Función para cargar imágenes
def load_image(filename):
    return pygame.image.load(os.path.join(assets, filename)).convert_alpha()

# Crear la pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.transform.scale(load_image("cielos.jpg").convert(),(800,600))
pygame.display.set_caption("Asteroids Game")

# Reloj para controlar la velocidad del juego
clock = pygame.time.Clock()

# Clase para representar la nave
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(load_image("jet_nofill.png").convert(), (80, 80))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0

# Clase para representar los asteroides
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(load_image("alien_nofill.png").convert(), (80, 80))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 8)
        self.speed_x = random.randrange(-3, 3)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 8)

# Función para mostrar texto en la pantalla
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Función para el juego
def game():
    score = 0
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    ship = Ship()
    all_sprites.add(ship)

    for i in range(3):
        asteroid = Asteroid()
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

    # Función para enviar datos a Firebase en un hilo aparte
    def update_database(action):
        Send_Data(action, Reference)

    # Game loop
    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    ship.speed_x = -5
                    threading.Thread(target=update_database, args=('left',)).start()  # Enviar datos a Firebase
                elif event.key == pygame.K_RIGHT:
                    ship.speed_x = 5
                    threading.Thread(target=update_database, args=('right',)).start()  # Enviar datos a Firebase
                elif event.key == pygame.K_UP:
                    bullet = Bullet(ship.rect.centerx, ship.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    threading.Thread(target=update_database, args=('Shot',)).start()  # Enviar datos a Firebase
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and ship.speed_x < 0:
                    ship.speed_x = 0
                elif event.key == pygame.K_RIGHT and ship.speed_x > 0:
                    ship.speed_x = 0

        # Actualizar
        all_sprites.update()

        # Colisiones entre balas y asteroides
        hits = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        for hit in hits:
            score += 5
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        # Colisiones entre nave y asteroides
        hits = pygame.sprite.spritecollide(ship, asteroids, True)
        if hits:
            running = False

        # Dibujar / renderizar
        screen.blit(background,(0,0))
        all_sprites.draw(screen)
        draw_text(screen, "Score: " + str(score), 30, WIDTH / 2, 10)
        pygame.display.flip()

        # Fijar FPS
        clock.tick(60)
      
# Clase para representar las balas
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(load_image("misil_nofill.png"),(50,50))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Función principal
if __name__ == "__main__":
    game()

pygame.quit()

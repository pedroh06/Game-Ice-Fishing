"""
=============================================================================
JOGO: ICE FISHING - Seminário Universitário de Computação Gráfica
=============================================================================
Autor: Gerado com fins acadêmicos
Biblioteca: Pygame
Tema: Inspirado no mini-game 'Ice Fishing' do Club Penguin

TRANSFORMAÇÕES GEOMÉTRICAS IMPLEMENTADAS:
------------------------------------------
1. TRANSLAÇÃO   → Classe Hook  → método update()
                  O anzol se move verticalmente no eixo Y com as setas
                  do teclado. A posição (rect.y) é incrementada/decrementada.

2. ROTAÇÃO      → Classe Hook  → método draw()
                  A imagem do anzol é rotacionada com pygame.transform.rotate()
                  simulando a resistência da água conforme se move.

3. ESCALA       → Classe Fish  → método apply_scale()
                  Ao colidir com o power-up, o peixe tem sua imagem
                  redimensionada com pygame.transform.scale().

4. REFLEXÃO     → Classe Fish  → método update()
                  Ao trocar de direção, a imagem é espelhada com
                  pygame.transform.flip(surface, flip_x=True, flip_y=False).

=============================================================================
"""

import pygame
import sys
import math
import random

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES GLOBAIS
# ---------------------------------------------------------------------------
SCREEN_WIDTH  = 700
SCREEN_HEIGHT = 600

FPS = 60

# Cores (R, G, B)
COLOR_SKY        = (180, 220, 255)   # Céu azul claro
COLOR_ICE        = (210, 240, 255)   # Gelo branco-azulado
COLOR_ICE_LINE   = (150, 200, 240)   # Linhas do gelo
COLOR_WATER      = (30,  80,  160)   # Água profunda
COLOR_WATER_DARK = (20,  55,  120)   # Água mais escura (fundo)
COLOR_WHITE      = (255, 255, 255)
COLOR_BLACK      = (0,   0,   0)
COLOR_YELLOW     = (255, 220,  50)
COLOR_RED        = (220,  50,  50)
COLOR_GREEN      = (50,  200, 100)
COLOR_ORANGE     = (255, 140,  30)
COLOR_PURPLE     = (160,  80, 200)
COLOR_HOOK_LINE  = (180, 140,  80)   # Cor da linha de pesca

# Divisória do gelo/água (eixo Y)
ICE_SURFACE_Y = 180

# Limites verticais do anzol
HOOK_Y_MIN = ICE_SURFACE_Y + 30
HOOK_Y_MAX = SCREEN_HEIGHT - 40

# Velocidade do anzol (translação)
HOOK_SPEED = 4

# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES DE DESENHO (superfícies procedurais)
# ---------------------------------------------------------------------------

def create_penguin_surface():
    """Cria a superfície do pinguim pescador desenhado com primitivas."""
    surf = pygame.Surface((60, 80), pygame.SRCALPHA)
    # Corpo
    pygame.draw.ellipse(surf, (30, 30, 30), (10, 20, 40, 55))
    # Barriga branca
    pygame.draw.ellipse(surf, COLOR_WHITE, (18, 30, 24, 38))
    # Cabeça
    pygame.draw.circle(surf, (30, 30, 30), (30, 18), 16)
    # Olhos
    pygame.draw.circle(surf, COLOR_WHITE, (24, 14), 5)
    pygame.draw.circle(surf, COLOR_WHITE, (36, 14), 5)
    pygame.draw.circle(surf, (0, 0, 0),   (25, 14), 3)
    pygame.draw.circle(surf, (0, 0, 0),   (37, 14), 3)
    # Bico
    pygame.draw.polygon(surf, COLOR_ORANGE, [(27, 20), (33, 20), (30, 26)])
    # Pés
    pygame.draw.ellipse(surf, COLOR_ORANGE, (8,  72, 16, 8))
    pygame.draw.ellipse(surf, COLOR_ORANGE, (36, 72, 16, 8))
    # Vareta de pesca (braço)
    pygame.draw.line(surf, (100, 70, 30), (48, 35), (60, 10), 3)
    return surf


def create_hook_surface():
    """Cria a superfície do anzol."""
    surf = pygame.Surface((20, 30), pygame.SRCALPHA)
    # Haste vertical
    pygame.draw.line(surf, (180, 180, 190), (10, 0), (10, 20), 3)
    # Curva do anzol
    pygame.draw.arc(surf, (180, 180, 190),
                    pygame.Rect(2, 14, 16, 14), math.pi, 2 * math.pi, 3)
    # Ponta
    pygame.draw.line(surf, (200, 200, 210), (18, 21), (18, 28), 3)
    return surf


def create_fish_surface(color, size=(60, 28)):
    """
    Cria a superfície de um peixe com a cor e tamanho indicados.
    Esta função é usada tanto na criação inicial quanto na ESCALA (transformação 3).
    """
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Corpo principal (elipse)
    pygame.draw.ellipse(surf, color, (0, h // 4, int(w * 0.75), h // 2))
    # Cauda (triângulo)
    tail_x = int(w * 0.72)
    pygame.draw.polygon(surf, color, [
        (tail_x, h // 2),
        (w,       h // 4),
        (w,       h * 3 // 4),
    ])
    # Olho
    eye_x = int(w * 0.12)
    eye_y = h // 2
    pygame.draw.circle(surf, COLOR_WHITE, (eye_x, eye_y), max(3, h // 9))
    pygame.draw.circle(surf, COLOR_BLACK, (eye_x, eye_y), max(1, h // 18))
    # Nadadeira dorsal
    pygame.draw.polygon(surf, color, [
        (int(w * 0.30), h // 4),
        (int(w * 0.45), 0),
        (int(w * 0.55), h // 4),
    ])
    return surf


def create_powerup_surface():
    """Cria a superfície do power-up (estrela dourada)."""
    surf = pygame.Surface((36, 36), pygame.SRCALPHA)
    cx, cy, r = 18, 18, 16
    points = []
    for i in range(10):
        angle = math.pi / 5 * i - math.pi / 2
        radius = r if i % 2 == 0 else r * 0.45
        points.append((cx + radius * math.cos(angle),
                        cy + radius * math.sin(angle)))
    pygame.draw.polygon(surf, COLOR_YELLOW, points)
    pygame.draw.polygon(surf, COLOR_ORANGE, points, 2)
    return surf

# ---------------------------------------------------------------------------
# SPRITES
# ---------------------------------------------------------------------------

class Fisherman(pygame.sprite.Sprite):
    """
    Pinguim pescador — fica estático no gelo.
    Não possui transformações geométricas diretas;
    serve de âncora visual para a linha de pesca.
    """

    def __init__(self):
        super().__init__()
        self.image = create_penguin_surface()
        self.rect  = self.image.get_rect()
        # Posicionado no centro superior, sobre o gelo
        self.rect.midbottom = (SCREEN_WIDTH // 2, ICE_SURFACE_Y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Hook(pygame.sprite.Sprite):
    """
    Anzol controlado pelo jogador.

    TRANSFORMAÇÕES IMPLEMENTADAS:
    ─────────────────────────────
    • TRANSLAÇÃO (T1):
        O anzol se desloca verticalmente no eixo Y.
        Implementação: self.pos_y += dy  →  self.rect.centery = int(self.pos_y)

    • ROTAÇÃO (T2):
        A imagem do anzol é rotacionada com pygame.transform.rotate().
        O ângulo oscila suavemente enquanto o anzol se move,
        simulando resistência da água.
    """

    def __init__(self, anchor_x):
        super().__init__()
        self.base_image = create_hook_surface()   # imagem original (sem rotação)
        self.image      = self.base_image.copy()
        self.rect       = self.image.get_rect()

        # Posição inicial: logo abaixo do buraco no gelo
        self.pos_y  = float(ICE_SURFACE_Y + 50)
        self.anchor_x = anchor_x                  # X fixo (alinhado ao pinguim)
        self.rect.centerx = anchor_x
        self.rect.centery = int(self.pos_y)

        # Estado de movimento (para controlar rotação)
        self.moving_down = False
        self.moving_up   = False

        # Ângulo atual de rotação (graus)
        self.angle       = 0.0
        # Acumulador de tempo para oscilar o ângulo suavemente
        self.time_acc    = 0.0

    # ------------------------------------------------------------------
    def update(self, keys, dt):
        """
        Atualiza posição (TRANSLAÇÃO) e ângulo (preparação para ROTAÇÃO).

        TRANSLAÇÃO — T1
        ───────────────
        Quando o jogador pressiona ↑ ou ↓, a posição Y do anzol é
        incrementada ou decrementada. Isso é a definição de translação:
            P' = P + vetor_deslocamento
        onde vetor_deslocamento = (0, ±HOOK_SPEED).
        """
        dy = 0

        if keys[pygame.K_DOWN]:
            dy = HOOK_SPEED          # ← TRANSLAÇÃO: desloca para baixo (+Y)
            self.moving_down = True
            self.moving_up   = False
        elif keys[pygame.K_UP]:
            dy = -HOOK_SPEED         # ← TRANSLAÇÃO: desloca para cima  (−Y)
            self.moving_down = False
            self.moving_up   = True
        else:
            self.moving_down = False
            self.moving_up   = False

        # Aplica o deslocamento e clipa nos limites da tela
        self.pos_y = max(HOOK_Y_MIN, min(HOOK_Y_MAX, self.pos_y + dy))
        self.rect.centery = int(self.pos_y)       # ← TRANSLAÇÃO aplicada ao rect
        self.rect.centerx = self.anchor_x

        # Atualiza o acumulador de tempo para calcular a oscilação do ângulo
        # A oscilação só ocorre enquanto o anzol está em movimento.
        if self.moving_down or self.moving_up:
            self.time_acc += dt
            # Função seno cria oscilação suave: ±8 graus
            # (simula resistência da água)
            self.angle = 8.0 * math.sin(self.time_acc * 3.5)
        else:
            # Retorna gradualmente ao ângulo neutro quando parado
            self.angle *= 0.85

    # ------------------------------------------------------------------
    def draw(self, surface):
        """
        Desenha a linha de pesca e o anzol com ROTAÇÃO aplicada.

        ROTAÇÃO — T2
        ─────────────
        pygame.transform.rotate(surface, angle) rotaciona a superfície
        ao redor de seu centro pelo ângulo informado (em graus, sentido
        anti-horário). O rect é recentrado após a rotação para evitar
        deslocamento visual (o Pygame expande o rect ao rotacionar).
        """
        # --- Linha de pesca (do pinguim até o anzol) ---
        start = (self.anchor_x, ICE_SURFACE_Y)
        end   = (self.rect.centerx, self.rect.centery)
        pygame.draw.line(surface, COLOR_HOOK_LINE, start, end, 2)

        # --- ROTAÇÃO: T2 ---
        # rotate() recebe a imagem original e o ângulo atual.
        # Usamos a imagem original (base_image) para evitar degradação
        # acumulada de qualidade a cada frame.
        rotated_image = pygame.transform.rotate(self.base_image, self.angle)

        # Após rotacionar, o rect muda de tamanho; reposicionamos pelo centro.
        rotated_rect = rotated_image.get_rect(center=self.rect.center)

        surface.blit(rotated_image, rotated_rect)


class Fish(pygame.sprite.Sprite):
    """
    Peixe que nada horizontalmente na água.

    TRANSFORMAÇÕES IMPLEMENTADAS:
    ─────────────────────────────
    • REFLEXÃO / FLIP (T4):
        Ao mudar de direção, a imagem é espelhada horizontalmente com
        pygame.transform.flip().

    • ESCALA (T3):
        Ao colidir com o power-up, apply_scale() aumenta o tamanho
        da imagem com pygame.transform.scale().
    """

    COLORS = [
        (220,  80,  80),   # vermelho
        (80,  160, 220),   # azul
        (80,  200, 120),   # verde
        (200, 120,  60),   # laranja
        (160,  80, 200),   # roxo
    ]

    def __init__(self):
        super().__init__()

        # Tamanho base do peixe
        self.base_w = random.randint(45, 70)
        self.base_h = int(self.base_w * 0.45)
        self.scale_factor = 1.0          # Fator de escala atual (cresce com power-up)

        color = random.choice(self.COLORS)
        self.color = color

        # Gera a imagem base (sem escala extra)
        self.base_image = create_fish_surface(color, (self.base_w, self.base_h))

        # Direção inicial: 1 → esquerda p/ direita | -1 → direita p/ esquerda
        self.direction = random.choice([-1, 1])
        self.speed     = random.uniform(1.5, 3.5)

        # Posição aleatória na área da água
        start_x = 0 if self.direction == 1 else SCREEN_WIDTH
        self.image = self.base_image.copy()
        self.rect  = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = random.randint(ICE_SURFACE_Y + 30, SCREEN_HEIGHT - 50)

        # Se o peixe nasce indo para a esquerda (direction = -1),
        # a imagem já deve estar espelhada desde o início.
        if self.direction == -1:
            # REFLEXÃO: T4 — espelha horizontalmente (flip_x=True)
            self.image = pygame.transform.flip(self.base_image, True, False)

        # Controle de captura
        self.captured = False
        # Controle de escala (para não aplicar escala repetidamente)
        self.scaled   = False

    # ------------------------------------------------------------------
    def update(self):
        """
        Move o peixe horizontalmente e aplica REFLEXÃO ao trocar de direção.

        REFLEXÃO — T4
        ─────────────
        pygame.transform.flip(surface, flip_x, flip_y)
            flip_x=True  → espelha no eixo vertical  (reflexão horizontal)
            flip_y=False → não espelha no eixo horizontal
        Isso simula o peixe "virando" ao mudar de sentido.
        """
        # Move horizontalmente conforme a direção
        self.rect.x += self.speed * self.direction

        # Verifica se saiu pela borda direita
        if self.direction == 1 and self.rect.left > SCREEN_WIDTH:
            self.direction = -1
            # ← REFLEXÃO (T4): peixe troca de direção → espelha a imagem
            self._apply_flip()
            self.rect.right = SCREEN_WIDTH

        # Verifica se saiu pela borda esquerda
        elif self.direction == -1 and self.rect.right < 0:
            self.direction = 1
            # ← REFLEXÃO (T4): peixe troca de direção → espelha a imagem
            self._apply_flip()
            self.rect.left = 0

    # ------------------------------------------------------------------
    def _apply_flip(self):
        """
        REFLEXÃO — T4 (método auxiliar)
        Atualiza self.image com a versão espelhada da imagem base escalada.
        Mantém a imagem base sem modificação para preservar qualidade.
        """
        # Calculamos o tamanho atual (pode ter sido escalado)
        current_w = int(self.base_w * self.scale_factor)
        current_h = int(self.base_h * self.scale_factor)

        # Recria a imagem base na escala atual
        scaled_base = pygame.transform.scale(
            self.base_image, (current_w, current_h)
        )

        if self.direction == -1:
            # Nadar para a esquerda → imagem espelhada (flip_x=True)
            # REFLEXÃO: T4
            self.image = pygame.transform.flip(scaled_base, True, False)
        else:
            # Nadar para a direita → imagem normal
            self.image = scaled_base

        # Mantém o centro do sprite após trocar a imagem
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)

    # ------------------------------------------------------------------
    def apply_scale(self, factor=2.0):
        """
        ESCALA — T3
        ─────────────────────────────────────────────────────────────────
        Aumenta o tamanho do peixe usando pygame.transform.scale().
        pygame.transform.scale(surface, (nova_largura, nova_altura))
        redimensiona a superfície para as dimensões fornecidas.

        Parâmetro:
            factor (float): multiplicador de tamanho (ex: 2.0 = dobro).
        """
        if self.scaled:
            return   # Já foi escalado; ignora nova colisão

        self.scale_factor *= factor
        self.scaled = True

        new_w = int(self.base_w * self.scale_factor)
        new_h = int(self.base_h * self.scale_factor)

        # ESCALA: T3 — redimensiona a imagem base para o novo tamanho
        scaled_img = pygame.transform.scale(self.base_image, (new_w, new_h))

        # Se o peixe está indo para a esquerda, mantém o flip aplicado
        if self.direction == -1:
            # REFLEXÃO composta com ESCALA
            self.image = pygame.transform.flip(scaled_img, True, False)
        else:
            self.image = scaled_img

        # Reposiciona mantendo o centro
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)


class PowerUp(pygame.sprite.Sprite):
    """
    Objeto power-up que nada na água.
    Quando um peixe colide com ele, o peixe sofre ESCALA (T3).
    O power-up também oscila verticalmente (movimento senoidal).
    """

    def __init__(self):
        super().__init__()
        self.base_image = create_powerup_surface()
        self.image      = self.base_image.copy()
        self.rect       = self.image.get_rect()
        self.rect.center = (
            random.randint(80, SCREEN_WIDTH - 80),
            random.randint(ICE_SURFACE_Y + 60, SCREEN_HEIGHT - 80)
        )
        self.origin_y   = float(self.rect.centery)
        self.time_acc   = random.uniform(0, math.pi * 2)   # fase aleatória
        self.active     = True

    def update(self, dt):
        """Oscila verticalmente com função seno (efeito flutuante)."""
        self.time_acc += dt * 2.0
        self.rect.centery = int(self.origin_y + 10 * math.sin(self.time_acc))

# ---------------------------------------------------------------------------
# CLASSE PRINCIPAL DO JOGO
# ---------------------------------------------------------------------------

class IceFishingGame:
    """
    Controlador principal do jogo.
    Gerencia o loop de eventos, atualização de sprites e renderização.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🐟 Ice Fishing — Computação Gráfica")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock  = pygame.time.Clock()

        # Fonte da UI
        self.font_big   = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 18)

        self._init_game()

    # ------------------------------------------------------------------
    def _init_game(self):
        """Inicializa/reinicia todos os objetos do jogo."""
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.fish_group  = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        # Cria o pinguim pescador
        self.fisherman = Fisherman()

        # Cria o anzol (ancorado no centro do pinguim)
        self.hook = Hook(anchor_x=self.fisherman.rect.centerx)

        # Cria peixes iniciais
        for _ in range(6):
            self._spawn_fish()

        # Cria o power-up inicial
        self._spawn_powerup()

        # Contador de peixes capturados
        self.score = 0

        # Tempo acumulado (segundos)
        self.elapsed = 0.0

        # Mensagem temporária na tela
        self.message      = ""
        self.message_timer = 0.0

        # Controle de estado
        self.game_over  = False
        self.paused     = False

    # ------------------------------------------------------------------
    def _spawn_fish(self):
        fish = Fish()
        self.fish_group.add(fish)
        self.all_sprites.add(fish)

    def _spawn_powerup(self):
        pu = PowerUp()
        self.powerup_group.add(pu)
        self.all_sprites.add(pu)

    # ------------------------------------------------------------------
    def _show_message(self, text, duration=1.5):
        self.message       = text
        self.message_timer = duration

    # ------------------------------------------------------------------
    def handle_events(self):
        """Processa todos os eventos do Pygame (teclado, janela, etc.)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self._init_game()    # Reinicia o jogo
                if event.key == pygame.K_p:
                    self.paused = not self.paused

    # ------------------------------------------------------------------
    def update(self, dt):
        """Atualiza a lógica do jogo a cada frame."""
        if self.paused or self.game_over:
            return

        self.elapsed += dt

        # Atualiza o temporizador de mensagem
        if self.message_timer > 0:
            self.message_timer -= dt

        # Lê o estado das teclas para controlar o anzol
        keys = pygame.key.get_pressed()

        # --- Atualiza o anzol (TRANSLAÇÃO + ROTAÇÃO) ---
        self.hook.update(keys, dt)

        # --- Atualiza os peixes (REFLEXÃO) ---
        for fish in self.fish_group:
            fish.update()

        # --- Atualiza os power-ups ---
        for pu in self.powerup_group:
            pu.update(dt)

        # --- Colisão: Anzol × Peixe ---
        self._check_hook_fish_collision()

        # --- Colisão: Peixe × Power-up ---
        self._check_fish_powerup_collision()

        # --- Reaparecimento de peixes (mantém quantidade mínima) ---
        if len(self.fish_group) < 5:
            self._spawn_fish()

        # --- Reaparecimento de power-up se coletado ---
        if len(self.powerup_group) == 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, 4000)   # 4s de delay

        # Spawna power-up via timer customizado
        for event in pygame.event.get(pygame.USEREVENT + 1):
            self._spawn_powerup()
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)       # cancela timer

    # ------------------------------------------------------------------
    def _check_hook_fish_collision(self):
        """
        Verifica colisão do anzol com peixes.
        Ao capturar um peixe, incrementa a pontuação e remove o sprite.
        """
        hook_rect = pygame.Rect(
            self.hook.rect.centerx - 8,
            self.hook.rect.centery - 8,
            16, 16
        )
        for fish in list(self.fish_group):
            if hook_rect.colliderect(fish.rect):
                size_bonus = " 🔥 GRANDE!" if fish.scaled else ""
                pts = 2 if fish.scaled else 1
                self.score += pts
                self._show_message(f"+{pts} peixe{size_bonus}", 1.2)
                fish.kill()
                self._spawn_fish()

    # ------------------------------------------------------------------
    def _check_fish_powerup_collision(self):
        """
        Verifica colisão de peixes com o power-up.

        ESCALA — T3
        ─────────────
        Ao colidir, chama fish.apply_scale() que usa
        pygame.transform.scale() para aumentar o sprite do peixe.
        """
        for pu in list(self.powerup_group):
            hit_fish = pygame.sprite.spritecollide(pu, self.fish_group, False)
            for fish in hit_fish:
                if not fish.scaled:
                    # ← ESCALA (T3): aplica redimensionamento no peixe
                    fish.apply_scale(factor=2.0)
                    self._show_message("⭐ Power-up! Peixe CRESCEU!", 1.8)
                    pu.kill()   # Remove o power-up após uso
                    break

    # ------------------------------------------------------------------
    def draw(self):
        """Renderiza todos os elementos na tela."""
        # --- Fundo: céu ---
        self.screen.fill(COLOR_SKY)

        # --- Gelo ---
        pygame.draw.rect(self.screen, COLOR_ICE,
                         (0, 0, SCREEN_WIDTH, ICE_SURFACE_Y))
        # Linhas decorativas no gelo
        for y in range(20, ICE_SURFACE_Y, 25):
            pygame.draw.line(self.screen, COLOR_ICE_LINE,
                             (0, y), (SCREEN_WIDTH, y), 1)

        # Buraco no gelo (onde a linha de pesca desce)
        hole_center = (self.fisherman.rect.centerx, ICE_SURFACE_Y)
        pygame.draw.ellipse(self.screen, COLOR_WATER_DARK,
                            (hole_center[0] - 18, hole_center[1] - 8, 36, 16))

        # --- Água ---
        pygame.draw.rect(self.screen, COLOR_WATER,
                         (0, ICE_SURFACE_Y, SCREEN_WIDTH,
                          SCREEN_HEIGHT - ICE_SURFACE_Y))

        # Efeito de profundidade da água (gradiente manual em faixas)
        for i in range(8):
            alpha_surf = pygame.Surface((SCREEN_WIDTH, 30), pygame.SRCALPHA)
            alpha = 20 + i * 8
            alpha_surf.fill((0, 0, 0, alpha))
            self.screen.blit(alpha_surf,
                             (0, ICE_SURFACE_Y + i * 30))

        # --- Peixes ---
        for fish in self.fish_group:
            self.screen.blit(fish.image, fish.rect)
            # Debug visual: contorno (pode comentar em produção)
            # pygame.draw.rect(self.screen, COLOR_WHITE, fish.rect, 1)

        # --- Power-ups ---
        for pu in self.powerup_group:
            self.screen.blit(pu.image, pu.rect)

        # --- Pinguim pescador ---
        self.fisherman.draw(self.screen)

        # --- Anzol (com linha e rotação) ---
        # ROTAÇÃO (T2) e TRANSLAÇÃO (T1) são aplicadas aqui
        self.hook.draw(self.screen)

        # --- Interface do usuário (UI) ---
        self._draw_ui()

        pygame.display.flip()

    # ------------------------------------------------------------------
    def _draw_ui(self):
        """Desenha a interface gráfica (pontuação, instruções, mensagens)."""

        # Painel de pontuação
        panel = pygame.Surface((220, 60), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        self.screen.blit(panel, (10, 10))

        score_surf = self.font_big.render(
            f"🐟 Peixes: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_surf, (18, 18))

        time_surf = self.font_small.render(
            f"Tempo: {int(self.elapsed)}s", True, (200, 230, 255))
        self.screen.blit(time_surf, (18, 46))

        # Instruções (canto inferior esquerdo)
        instructions = [
            "↑↓ : Mover anzol",
            "R  : Reiniciar",
            "P  : Pausar",
            "ESC: Sair",
        ]
        for i, line in enumerate(instructions):
            surf = self.font_small.render(line, True, (200, 230, 255))
            self.screen.blit(surf, (10, SCREEN_HEIGHT - 90 + i * 20))

        # Legenda das transformações (canto superior direito)
        legend_lines = [
            ("T1 TRANSLAÇÃO", (100, 200, 255)),
            ("T2 ROTAÇÃO",    (255, 220, 100)),
            ("T3 ESCALA",     (100, 255, 150)),
            ("T4 REFLEXÃO",   (255, 130, 130)),
        ]
        lx = SCREEN_WIDTH - 180
        legend_panel = pygame.Surface((175, 90), pygame.SRCALPHA)
        legend_panel.fill((0, 0, 0, 130))
        self.screen.blit(legend_panel, (lx - 5, 8))

        for i, (text, color) in enumerate(legend_lines):
            surf = self.font_small.render(text, True, color)
            self.screen.blit(surf, (lx, 12 + i * 20))

        # Mensagem temporária (centro da tela)
        if self.message and self.message_timer > 0:
            msg_surf = self.font_big.render(self.message, True, COLOR_YELLOW)
            msg_rect = msg_surf.get_rect(
                center=(SCREEN_WIDTH // 2, ICE_SURFACE_Y + 60))
            # Sombra
            shadow = self.font_big.render(self.message, True, COLOR_BLACK)
            self.screen.blit(shadow, (msg_rect.x + 2, msg_rect.y + 2))
            self.screen.blit(msg_surf, msg_rect)

        # Estado de pausa
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))
            pause_surf = self.font_big.render("⏸ PAUSADO", True, COLOR_WHITE)
            pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                     SCREEN_HEIGHT // 2))
            self.screen.blit(pause_surf, pause_rect)

    # ------------------------------------------------------------------
    def run(self):
        """Loop principal do jogo."""
        while True:
            # dt = delta time em segundos (para movimentos independentes de FPS)
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()


# ---------------------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    game = IceFishingGame()
    game.run()

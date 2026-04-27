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
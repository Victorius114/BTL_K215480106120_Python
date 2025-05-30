import pygame
import sys
import math
from entities import Player, Enemy, Platform, Boss


def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Platformer Game")
    clock = pygame.time.Clock()

    def load_image(path):
        return pygame.transform.scale(pygame.image.load(path), (WIDTH, HEIGHT))

    # Tạo platform từng level
    platforms_levels = [
        [Platform(200, 450, 200, 20), Platform(500, 400, 150, 20)],
        [Platform(150, 400, 150, 20), Platform(600, 350, 200, 20)],
        [Platform(100, 450, 100, 20), Platform(300, 350, 100, 20), Platform(500, 450, 100, 20)],
        [Platform(200, 500, 100, 20), Platform(400, 400, 100, 20), Platform(600, 300, 100, 20)],
        [Platform(100, 550, 600, 20), Platform(350, 400, 255, 20)]
    ]

    levels = [
        [Enemy(220, 450 - 64), Enemy(520, 400 - 64)],
        [Enemy(170, 400 - 64), Enemy(620, 350 - 64)],
        [Enemy(120, 450 - 64), Enemy(320, 350 - 64), Enemy(520, 450 - 64)],
        [Enemy(220, 500 - 64), Enemy(420, 400 - 64), Enemy(620, 300 - 64)],
        [Boss(350, 400 - 64)]
    ]

    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)

    def draw_text(text, x, y, color=(255, 255, 255), center=False, font_obj=None):
        font_to_use = font_obj if font_obj else font
        img = font_to_use.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        screen.blit(img, rect)

    # Trạng thái
    in_menu = True
    game_over = False
    game_win = False

    current_level = 0
    enemies = levels[current_level]
    platforms = platforms_levels[current_level]
    player = Player(50, 500)

    while True:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Hiển thị menu chính
        if in_menu:
            screen.blit(load_image(f"textures/title.jpg"), (0, 0))  # Dùng title.jpg làm nền menu
            draw_text("Press ENTER to start", WIDTH // 2, 550, (255, 0, 0), center=True)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    in_menu = False
            continue

        if game_over:
            screen.fill((0, 0, 0))
            draw_text("YOU LOST!", WIDTH // 2, HEIGHT // 2 - 40, (255, 0, 0), center=True, font_obj=big_font)
            draw_text("Press ESC to quit", WIDTH // 2, HEIGHT // 2 + 20, (255, 255, 255), center=True)
            pygame.display.flip()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            continue

        if game_win:
            screen.fill((0, 0, 0))
            draw_text("YOU WON!", WIDTH // 2, HEIGHT // 2 - 40, (0, 255, 0), center=True, font_obj=big_font)
            draw_text("Press ESC to quit", WIDTH // 2, HEIGHT // 2 + 20, (255, 255, 255), center=True)
            pygame.display.flip()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            continue

        # Cập nhật
        player.update(keys, platforms)
        for enemy in enemies:
            if enemy.alive:
                enemy.update(platforms)

        player_hitbox = player.get_hitbox()
        for enemy in enemies:
            for bullet in enemy.bullets[:]:
                if bullet.rect.colliderect(player_hitbox):
                        enemy.bullets.remove(bullet)
                        if not player.invincible:
                            player.health -= 1
                            player.invincible = True
                            player.invincibility_timer = 60
                            if player.health <= 0:
                                game_over = True

        if player.is_attacking:
            attack_hitbox = player.get_attack_hitbox()
            for enemy in enemies[:]:
                if enemy.alive and attack_hitbox.colliderect(enemy.get_hitbox()):
                    if isinstance(enemy, Boss):
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                    else:
                        enemies.remove(enemy)

        if len(enemies) == 0 and player.x >= WIDTH - player.width:
            current_level += 1
            if current_level < len(levels):
                enemies = levels[current_level]
                platforms = platforms_levels[current_level]
                player.x = 50
                player.y = 500
            else:
                game_win = True

        # Vẽ
        screen.fill((30, 30, 30))
        for plat in platforms:
            plat.draw(screen)

        for enemy in enemies:
            if enemy.alive:
                enemy.draw(screen)

        player.draw(screen)

        for enemy in enemies:
            for bullet in enemy.bullets:
                bullet.draw(screen)

        draw_text(f"HP: {player.health}", 10, 10)
        draw_text(f"Level: {current_level + 1}/{len(levels)}", 10, 50)

        if current_level == 4 and len(enemies) > 0 and isinstance(enemies[0], Boss):
            boss = enemies[0]
            draw_text(f"BOSS HP: {boss.health}", WIDTH // 2 - 60, 10)

        pygame.display.flip()


if __name__ == "__main__":
    main()

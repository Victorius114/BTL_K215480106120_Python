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

    # Tạo platform từng level
    platforms_levels = [
        # Level 1
        [Platform(200, 450, 200, 20), Platform(500, 400, 150, 20)],
        # Level 2
        [Platform(150, 400, 150, 20), Platform(600, 350, 200, 20)],
        # Level 3
        [Platform(100, 450, 100, 20), Platform(300, 350, 100, 20), Platform(500, 450, 100, 20)],
        # Level 4
        [Platform(200, 500, 100, 20), Platform(400, 400, 100, 20), Platform(600, 300, 100, 20)],
        # Level 5 (Boss)
        [Platform(100, 550, 600, 20), Platform(350, 400, 100, 20)]
    ]

    # Enemy spawn trên platform
    levels = [
        # Level 1
        [Enemy(220, 450 - 64), Enemy(520, 400 - 64)],
        # Level 2
        [Enemy(170, 400 - 64), Enemy(620, 350 - 64)],
        # Level 3
        [Enemy(120, 450 - 64), Enemy(320, 350 - 64), Enemy(520, 450 - 64)],
        # Level 4
        [Enemy(220, 500 - 64), Enemy(420, 400 - 64), Enemy(620, 300 - 64)],
        # Level 5 (Boss)
        [Boss(350, 400 - 64)]
    ]

    current_level = 0
    enemies = levels[current_level]
    platforms = platforms_levels[current_level]

    player = Player(50, 500)

    font = pygame.font.SysFont(None, 36)
    game_over = False
    game_win = False

    def draw_text(text, x, y, color=(255, 255, 255)):
        img = font.render(text, True, color)
        screen.blit(img, (x, y))

    while True:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if game_over:
            screen.fill((0, 0, 0))
            draw_text("GAME OVER", WIDTH // 2 - 80, HEIGHT // 2)
            pygame.display.flip()
            continue

        if game_win:
            screen.fill((0, 0, 0))
            draw_text("YOU WIN!", WIDTH // 2 - 80, HEIGHT // 2)
            pygame.display.flip()
            continue

        # Update player và enemies
        player.update(keys, platforms)
        for enemy in enemies:
            if enemy.alive:
                enemy.update(platforms)

        # Kiểm tra đạn của enemy trúng player
        player_hitbox = player.get_hitbox()
        shield_hitbox = player.get_shield_hitbox()
        for enemy in enemies:
            for bullet in enemy.bullets[:]:
                if bullet.rect.colliderect(player_hitbox):
                    if player.shield_active and shield_hitbox and bullet.rect.colliderect(shield_hitbox):
                        enemy.bullets.remove(bullet)
                    else:
                        enemy.bullets.remove(bullet)
                        if not player.invincible:
                            player.health -= 1
                            player.invincible = True
                            player.invincibility_timer = 60
                            if player.health <= 0:
                                game_over = True

        # Kiểm tra đòn đánh player trúng enemy
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

        # Kiểm tra chuyển màn
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

        # Vẽ đạn của enemy
        for enemy in enemies:
            for bullet in enemy.bullets:
                bullet.draw(screen)

        # HUD
        draw_text(f"HP: {player.health}", 10, 10)
        draw_text(f"Level: {current_level + 1}/{len(levels)}", 10, 50)

        # Hiển thị máu boss nếu là màn boss
        if current_level == 4 and len(enemies) > 0 and isinstance(enemies[0], Boss):
            boss = enemies[0]
            draw_text(f"BOSS HP: {boss.health}", WIDTH // 2 - 60, 10)

        pygame.display.flip()


if __name__ == "__main__":
    main()
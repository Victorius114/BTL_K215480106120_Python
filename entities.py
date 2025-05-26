import time

import pygame
import os
import math

def load_image(name):
    path = os.path.join("textures", name)
    return pygame.transform.scale(pygame.image.load(path), (64, 64))

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)

    def get_hitbox(self):
        return self.rect


class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.speed = 6 * direction
        self.rect = pygame.Rect(self.x, self.y, 16, 8)
        self.alive = True

    def update(self):
        self.x += self.speed
        self.rect.x = self.x
        # Nếu viên đạn bay ra khỏi màn hình, hủy
        if self.x < 0 or self.x > 800:
            self.alive = False

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), self.rect)

class BossBullet:
    def __init__(self, x, y, x_speed, y_speed):
        self.x = x
        self.y = y
        self.speed_x = x_speed
        self.speed_y = y_speed
        self.rect = pygame.Rect(self.x, self.y, 16, 8)
        self.alive = True

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 600:
            self.alive = False

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 255), self.rect)

class Gun:
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.image = pygame.image.load(f'textures/gun.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))
        self.picked_up = False

    def update(self, player):
        if not self.picked_up and self.rect.colliderect(player.rect):
            self.picked_up = True
            player.has_gun = True
            player.gun_timer = time.time()

    def draw(self, surface):
        if not self.picked_up:
            surface.blit(self.image, self.rect)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.vel_y = 0
        self.speed = 3
        self.gravity = 0.5
        self.jump_power = 15
        self.is_jumping = False
        self.facing_right = True
        self.health = 10
        self.is_attacking = False
        self.attack_duration = 10
        self.attack_timer = 1
        self.invincible = False
        self.invincibility_timer = 0
        self.shield_active = False
        self.shield_cooldown = 0
        self.attack_cooldown = 0
        self.attack_ready = True
        self.attack_key_released = True
        self.has_gun = False
        self.gun_timer = 0
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 500
        self.last_shot_time = 0

        # Load images
        self.idle_img = load_image("char.png")
        self.idle_img_left = pygame.transform.flip(self.idle_img, True, False)

        self.move_images_right = [load_image(f"char_move_{i}.png") for i in range(1, 4)]
        self.move_images_left = [pygame.transform.flip(img, True, False) for img in self.move_images_right]

        self.attack_images_right = [load_image("char_atk_1.png"), load_image("char_atk_2.png")]
        self.attack_images_left = [pygame.transform.flip(img, True, False) for img in self.attack_images_right]

        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 10
        self.current_img = self.idle_img

        self.attack_anim_index = 0
        self.attack_anim_timer = 0
        self.attack_anim_speed = 5

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_attack_hitbox(self):
        if self.is_attacking:
            if self.facing_right:
                return pygame.Rect(self.x + self.width, self.y + 16, 32, 32)
            else:
                return pygame.Rect(self.x - 32, self.y + 16, 32, 32)
        return None

    def get_shield_hitbox(self):
        if self.shield_active:
            if self.facing_right:
                return pygame.Rect(self.x + self.width, self.y + 10, 40, self.height - 20)
            else:
                return pygame.Rect(self.x - 40, self.y + 10, 40, self.height - 20)
        return None

    def update(self, keys, platforms):
        moving = False

        if keys[pygame.K_UP] and not self.is_jumping:
            self.is_jumping = True
            self.vel_y = -self.jump_power

        if keys[pygame.K_z] and self.attack_ready and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_ready = False
            self.attack_cooldown = 10

        if not keys[pygame.K_z]:
            self.attack_key_released = True

        if keys[pygame.K_z] and self.attack_key_released and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_key_released = False
            self.attack_cooldown = 10

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if keys[pygame.K_x] and self.shield_cooldown <= 0:
            self.shield_active = True
        else:
            self.shield_active = False

        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        if self.shield_active:
            self.shield_cooldown = 240

        if keys[pygame.K_LEFT]:
            if self.x > 0:
                self.x -= self.speed
                self.facing_right = False
                moving = True
        elif keys[pygame.K_RIGHT]:
            if self.x < 800 - self.width:
                self.x += self.speed
                self.facing_right = True
                moving = True

        self.vel_y += self.gravity
        self.y += self.vel_y

        on_platform = False
        player_rect = self.get_hitbox()
        for plat in platforms:
            if player_rect.colliderect(plat.rect):
                if self.vel_y >= 0 and player_rect.bottom - self.vel_y <= plat.rect.top:
                    self.y = plat.rect.top - self.height
                    self.vel_y = 0
                    self.is_jumping = False
                    on_platform = True

        if not on_platform and self.y < 500:
            self.is_jumping = True

        if self.y >= 500:
            self.y = 500
            self.vel_y = 0
            self.is_jumping = False

        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_anim_index = 0
                self.attack_anim_timer = 0

        if self.has_gun and (time.time() - self.gun_timer > 5):
            self.has_gun = False

        # Animation
        if self.is_attacking:
            self.attack_anim_timer += 1
            if self.attack_anim_timer >= self.attack_anim_speed:
                self.attack_anim_timer = 0
                self.attack_anim_index = (self.attack_anim_index + 1) % len(self.attack_images_right)
            self.current_img = (
                self.attack_images_right[self.attack_anim_index]
                if self.facing_right
                else self.attack_images_left[self.attack_anim_index]
            )
        elif moving:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.move_images_right)
            self.current_img = (
                self.move_images_right[self.anim_index]
                if self.facing_right
                else self.move_images_left[self.anim_index]
            )
        else:
            self.current_img = self.idle_img if self.facing_right else self.idle_img_left
            self.anim_index = 0
            self.anim_timer = 0

    def shoot(self, direction):
        current_time = pygame.time.get_ticks()
        if self.has_gun and current_time - self.last_shot_time > self.shoot_cooldown:
            bullet = Bullet(self.x + self.width // 2, self.y + self.height // 2, direction)
            self.bullets.add(bullet)
            self.last_shot_time = current_time

    def draw(self, screen):
        screen.blit(self.current_img, (self.x, self.y))


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.speed = 1.5
        self.direction = 1
        self.alive = True
        self.img = load_image("enemy.png")
        self.img_left = pygame.transform.flip(self.img, True, False)
        self.bullets = []
        self.shoot_cooldown = 120  # 2 giây
        self.shoot_timer = 0

        self.vel_y = 0
        self.gravity = 0.5
        self.is_jumping = False

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, platforms):
        if not self.alive:
            return

        # Di chuyển ngang
        self.x += self.speed * self.direction

        # Rẽ trái phải khi chạm giới hạn (300 - 700)
        if self.x < 300:
            self.direction = 1
        elif self.x > 700 - self.width:
            self.direction = -1

        # Trọng lực và va chạm platform
        self.vel_y += self.gravity
        self.y += self.vel_y

        enemy_rect = self.get_hitbox()
        on_platform = False
        for plat in platforms:
            if enemy_rect.colliderect(plat.rect):
                # Chỉ xử lý khi rơi xuống chạm platform
                if self.vel_y >= 0 and enemy_rect.bottom - self.vel_y <= plat.rect.top:
                    self.y = plat.rect.top - self.height
                    self.vel_y = 0
                    self.is_jumping = False
                    on_platform = True
        if not on_platform and self.y < 500:
            self.is_jumping = True

        if self.y >= 500:
            self.y = 500
            self.vel_y = 0
            self.is_jumping = False

        # Bắn đạn
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        else:
            self.shoot()
            self.shoot_timer = self.shoot_cooldown

        # Update bullets
        for bullet in self.bullets:
            bullet.update()
        # Xóa đạn không còn alive
        self.bullets = [b for b in self.bullets if b.alive]

    def shoot(self):
        # Bắn đạn theo hướng đang đi
        direction = self.direction
        bullet_x = self.x + (self.width if direction == 1 else -16)
        bullet_y = self.y + self.height // 2
        self.bullets.append(Bullet(bullet_x, bullet_y, direction))

    def draw(self, screen):
        if self.alive:
            img = self.img if self.direction == 1 else self.img_left
            screen.blit(img, (self.x, self.y))

        for bullet in self.bullets:
            bullet.draw(screen)


class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 96  # Lớn hơn enemy thường
        self.height = 96
        self.health = 100
        self.max_health = 100
        self.speed = 2  # Tốc độ di chuyển
        self.boss_img = pygame.transform.scale(load_image("boss.png"), (self.width, self.height))
        self.boss_img_left = pygame.transform.flip(self.boss_img, True, False)
        self.vel_x = 1
        self.attack_pattern = 0
        self.pattern_timer = 0
        self.shoot_cooldown = 30  # Nhanh hơn enemy thường

    def update(self, platforms):
        # Di chuyển theo pattern
        self.pattern_timer += 1
        v =2.7

        if self.pattern_timer > 180:  # Đổi pattern sau 3 giây
            self.pattern_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3

        # Pattern 0: Di chuyển qua lại
        if self.attack_pattern == 0:
            self.x += self.vel_x
            if self.x <= 100 or self.x >= 600:
                self.vel_x *= -1
                self.direction = 1 if self.vel_x > 0 else -1

        # Pattern 1: Đứng yên bắn đạn 8 hướng
        elif self.attack_pattern == 1:
            if self.pattern_timer % 60 == 0:  # Bắn đạn mỗi 20 frame
                for angle in range(0, 360, 45):  # Bắn 8 hướng
                    rad = math.radians(angle)
                    self.bullets.append(BossBullet(
                        self.x + self.width // 2,
                        self.y + self.height // 2,
                        v * math.cos(rad),
                        v * math.sin(rad)
                    ))


        # Pattern 2: Nhảy
        elif self.attack_pattern == 2 and self.pattern_timer == 1:
            self.vel_y = -20

        # Áp dụng trọng lực
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10

        self.y += self.vel_y

        # Kiểm tra va chạm với platform
        boss_rect = self.get_hitbox()
        for plat in platforms:
            plat_rect = plat.get_hitbox()
            if boss_rect.colliderect(plat_rect):
                if self.vel_y > 0 and self.y + self.height > plat.rect.top and self.y < plat.rect.top:
                    self.y = plat.rect.top - self.height
                    self.vel_y = 0

        # Cập nhật đạn
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.alive:
                self.bullets.remove(bullet)

    def draw(self, screen):
        # Vẽ boss
        img = self.boss_img if self.direction == 1 else self.boss_img_left
        screen.blit(img, (self.x, self.y))

        # Vẽ đạn
        for bullet in self.bullets:
            bullet.draw(screen)

        # Vẽ thanh máu
        health_width = int(self.width * (self.health / self.max_health))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 20, self.width, 10))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 20, health_width, 10))

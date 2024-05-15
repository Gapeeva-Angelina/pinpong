# команда для сборки игры в один исходный файл
# pyinstaller --onefile --name MyGame --icon=icon.ico -F --noconsole main5.py

import pygame as PG
import sys
from random import randint
PG.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN = PG.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
FPS = 60
CLOCK = PG.time.Clock()

PG.mixer.init()

MUSIC_END = PG.USEREVENT + 1
PG.mixer.music.set_endevent(MUSIC_END)

bg_music_play_list = [
    './src/music/bgm_space_1.mp3',
    './src/music/bgm_space_2.mp3',
    './src/music/bgm_space_3.mp3',
    './src/music/bgm_space_4.mp3',
    './src/music/bgm_space_5.mp3',
    './src/music/bgm_space_6.mp3',
    './src/music/bgm_space_7.mp3',
    './src/music/bgm_space_8.mp3',
]  
bg_music_index = randint(0, len(bg_music_play_list) - 1)

def bg_music_play():
    global bg_music_index
    bg_music_index += 1
    if bg_music_index == len(bg_music_play_list) : bg_music_index = 0
    music = bg_music_play_list[bg_music_index] 

    PG.mixer.music.load(music)
    PG.mixer.music.set_volume(0.7)
    PG.mixer.music.play()

bg_music_play()


sound_hit_1 = PG.mixer.Sound('./src/sounds/se_hit.mp3')
sound_hit_2 = PG.mixer.Sound('./src/sounds/se_rock.mp3')

PG.mixer.music.load('./src/music/bgm_space_4.mp3')
PG.mixer.music.set_volume(0.7)
PG.mixer.music.play()

bg_image = PG.image.load('./src/images/space_bg_tile_1524x802px.jpg')
#bg_image = PG.transform.scale( bg_image, (960, 701) )
bg_draw_point = (-(1524 - SCREEN_WIDTH) / 2, -(802 - SCREEN_HEIGHT) / 2)

ball_image = PG.image.load('./src/images/ball_116x116px.png')
ball_image = PG.transform.scale( ball_image, (32, 32) )

player_left_image = PG.image.load('./src/images/p1_128x512px.png')
player_left_image = PG.transform.scale( player_left_image, (32, 128) )

player_right_image = PG.image.load('./src/images/p2_128x512px.png')
player_right_image = PG.transform.scale( player_right_image, (32, 128) )

win_score = 10

class Label():
    def __init__(self, text, x, y, align = 'left', font_size = 36, color = (255, 255, 255)):
        self.font = PG.font.Font(None, font_size)
        self.align = align
        self.color = color
        self.x = x
        self.y = y
        self.render(text)
    
    def render(self, text):
        self.text = self.font.render(text, True, self.color)
        self.rect = self.text.get_rect()
        self.rect.centery = self.y
        if self.align == 'left': self.rect.left = self.x
        elif self.align == 'right': self.rect.right = self.x
        else : self.rect.centerx = self.x

class Ball(PG.sprite.Sprite):
    def __init__(self):
        PG.sprite.Sprite.__init__(self)
        self.image = ball_image
        self.rect = self.image.get_rect()
        self.restart()

    def move(self):
        self.rect.centerx += self.speed_x
        self.rect.centery += self.speed_y

        if self.rect.top < 0:
            sound_hit_1.play()
            self.rect.top = 0
            self.speed_y *= -1

        elif self.rect.bottom > SCREEN_HEIGHT:
            sound_hit_1.play()
            self.rect.bottom = SCREEN_HEIGHT
            self.speed_y *= -1

        elif self.rect.x < 0:
            sound_hit_2.play()
            p2.get_score()
            self.restart()

        elif self.rect.right > SCREEN_WIDTH:
            sound_hit_2.play()
            p1.get_score()
            self.restart()

        elif self.rect.colliderect(p1.rect):
            sound_hit_1.play()
            self.rect.left = p1.rect.right
            self.speed_x *= -1

        elif self.rect.colliderect(p2.rect):
            sound_hit_1.play()
            self.rect.right = p2.rect.left
            self.speed_x *= -1

    def restart(self):
        self.rect.centerx = SCREEN_WIDTH * 0.5
        self.rect.centery = SCREEN_HEIGHT * 0.5
        self.speed_x = 5 if randint(0, 1) == 1 else -5
        self.speed_y = 5 if randint(0, 1) == 1 else -5

    def update(self):
        self.move()
        SCREEN.blit(self.image, self.rect)

class Player(PG.sprite.Sprite):
    def __init__(self, is_left):
        PG.sprite.Sprite.__init__(self)
        self.image = player_left_image if is_left else player_right_image
        self.rect = self.image.get_rect()
        self.rect.x = 0 if is_left else SCREEN_WIDTH - self.rect.width
        self.rect.centery = SCREEN_HEIGHT * 0.5
        self.score = 0
        self.speed = 5
        self.bot_speed = 3
        self.is_player = True
        if is_left :
            self.score_label = Label(f'Score: {self.score}', 15, 30, 'left', 36, (0, 255, 255))
            self.win_label = Label('Player left win!', SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5, 'center', 120, (0, 255, 255))
        else :
            self.score_label = Label(f'Score: {self.score}', SCREEN_WIDTH - 15, 30, 'right', 36, (255, 0, 255))
            self.win_label = Label('Player right win!', SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5, 'center', 120, (255, 0, 255))

    def get_score(self):
        self.score += 1
        self.score_label.render(f'Score: {self.score}')
    
    def bot_move(self):
        if ball.rect.centery > self.rect.centery : self.rect.centery += self.bot_speed
        elif ball.rect.centery < self.rect.centery : self.rect.centery -= self.bot_speed

class Player_left(Player):
    def __init__(self):
        super().__init__(True)

    def update(self):
        if self.is_player:
            KEY = PG.key.get_pressed()
            if KEY[PG.K_w]:
                self.rect.y -= self.speed
                if self.rect.y < 0 : self.rect.y = 0
            elif KEY[PG.K_s]:
                self.rect.y += self.speed
                if self.rect.bottom > SCREEN_HEIGHT : self.rect.bottom = SCREEN_HEIGHT
        else:
            self.bot_move()
        
        SCREEN.blit(self.image, self.rect)
        SCREEN.blit(self.score_label.text, self.score_label.rect)
    
class Player_Right(Player):
    def __init__(self):
        super().__init__(False)

    def update(self):
        if self.is_player:
            KEY = PG.key.get_pressed()
            if KEY[PG.K_UP]:
                self.rect.y -= self.speed
                if self.rect.y < 0 : self.rect.y = 0
            elif KEY[PG.K_DOWN]:
                self.rect.y += self.speed
                if self.rect.bottom > SCREEN_HEIGHT : self.rect.bottom = SCREEN_HEIGHT
        else:
            self.bot_move()

        SCREEN.blit(self.image, self.rect)
        SCREEN.blit(self.score_label.text, self.score_label.rect) 
 
p1 = Player_left()
p2 = Player_Right()
ball = Ball()

tick = 0 # создаем счетчик кадров
game_loop_is = True

# ГЛАВНыЙ ЦИКЛ ИГРЫ
while game_loop_is:
    CLOCK.tick(FPS)
    tick += 1

    for event in PG.event.get():
        if event.type == PG.QUIT or (event.type == PG.KEYDOWN and event.key == PG.K_ESCAPE):
            game_loop_is = False
        elif event.type == PG.KEYUP and event.key == PG.K_1 : p1.is_player = not p1.is_player
        elif event.type == PG.KEYUP and event.key == PG.K_2 : p2.is_player = not p2.is_player
        elif event.type == MUSIC_END : bg_music_play()

    SCREEN.blit(bg_image, bg_draw_point)
    if p1.score >= win_score :
        SCREEN.blit(p1.win_label.text, p1.win_label.rect)
        SCREEN.blit(p1.score_label.text, p1.score_label.rect)
        SCREEN.blit(p2.score_label.text, p2.score_label.rect)
    elif p2.score >= win_score :
        SCREEN.blit(p2.win_label.text, p2.win_label.rect)
        SCREEN.blit(p1.score_label.text, p1.score_label.rect)
        SCREEN.blit(p2.score_label.text, p2.score_label.rect)
    else:
        p1.update()
        p2.update()
        ball.update()

    PG.display.flip()

PG.quit()
sys.exit()
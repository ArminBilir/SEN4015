import pygame
import random
import sys
import threading
import sqlite3
import customtkinter as ctk


def create_database():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            highscore INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Skorkaydetme
def save(nickname, score):
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute('SELECT highscore FROM scores WHERE nickname = ?', (nickname,))
    result = c.fetchone()

    if result:
        if score > result[0]:
            c.execute('UPDATE scores SET highscore = ? WHERE nickname = ?', (score, nickname))
    else:
        c.execute('INSERT INTO scores (nickname, highscore) VALUES (?, ?)', (nickname, score))

    conn.commit()
    conn.close()

# Skorlarıgör
def show_scores():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute('SELECT nickname, highscore FROM scores ORDER BY highscore DESC')
    scores = c.fetchall()
    conn.close()

    scores_text = ""
    for score in scores:
        scores_text += f"{score[0]}: {score[1]}\n"

    return scores_text

pygame.init()
pygame.mixer.init()

#dışardan aldığım wav dosyaları
jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")

screen = pygame.display.set_mode((548, 400))
# Screen dimensions
WIDTH = 548
HEIGHT = 400
FPS = 60
# dışardan aldıgım görseller
background_img = pygame.image.load("assets/images/background.png").convert()
bird_img_raw = pygame.image.load("assets/images/bird.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img_raw, (40, 30))
pipe_img_raw = pygame.image.load("assets/images/pipe.png").convert_alpha()
pipe_img = pygame.transform.scale(pipe_img_raw, (70, 400))
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

gravity = 0.5
jump_strength = -10
pipe_width = 70
pipe_velocity = -4
pipe_spacing_range = (250, 350)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 32)

# kuş
class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 15

    def update(self):
        self.velocity += gravity
        self.y += self.velocity

    def jump(self):
        self.velocity = jump_strength

    def draw(self):
        screen.blit(bird_img, (int(self.x - bird_img.get_width() // 2), int(self.y - bird_img.get_height() // 2)))


# pipelar
class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.height = random.randint(50, HEIGHT - 200)
        self.gap = random.randint(120, 180)

    def update(self):
        self.x += pipe_velocity

    def draw(self):
        top_pipe = pygame.transform.flip(pipe_img, False, True)
        screen.blit(top_pipe, (self.x, self.height - top_pipe.get_height()))
        screen.blit(pipe_img, (self.x, self.height + self.gap))

    def collide(self, bird):
        if bird.x + bird.radius > self.x and bird.x - bird.radius < self.x + pipe_width:
            if bird.y - bird.radius < self.height or bird.y + bird.radius > self.height + self.gap:
                return True
        return False
def game_loop(nickname):
    bird = Bird()
    pipes = [Pipe()]
    score = 0
    running = True
    game_over = False
    started = False
    random_spacing = random.randint(*pipe_spacing_range)
    bg_x = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not started:
                        started = True
                    bird.jump()
                    jump_sound.play()
                if event.key == pygame.K_r and game_over:
                    save(nickname, score)
                    return

        if not game_over and started:
            bird.update()
            if pipes[-1].x < WIDTH - random_spacing:
                pipes.append(Pipe())
                random_spacing = random.randint(*pipe_spacing_range)
            for pipe in pipes:
                pipe.update()
                if pipe.collide(bird):
                    hit_sound.play()
                    game_over = True
                if pipe.x + pipe_width < bird.x and not hasattr(pipe, 'scored'):
                    score += 1
                    pipe.scored = True

            pipes = [pipe for pipe in pipes if pipe.x + pipe_width > 0]

            if bird.y > HEIGHT or bird.y < 0:
                hit_sound.play()
                game_over = True
        bg_x -= 1
        if bg_x <= -WIDTH:
            bg_x = 0
        screen.blit(background_img, (bg_x, 0))
        screen.blit(background_img, (bg_x + WIDTH, 0))

        bird.draw()
        for pipe in pipes:
            pipe.draw()

        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        if not started and not game_over:
            start_text = font.render("Press SPACE to Start", True, (0, 0, 0))
            screen.blit(start_text, (WIDTH // 2 - 150, HEIGHT // 2 - 20))

        if game_over:
            game_over_text = font.render("Game Over! Press R", True, (255, 0, 0))
            screen.blit(game_over_text, (WIDTH // 2 - 160, HEIGHT // 2 - 20))

        pygame.display.flip()


def launch_game(nickname):
    app.withdraw()
    while True:
        game_loop(nickname)
        break
    app.deiconify()
def show_scores_window():
    scores_text = show_scores()

    scores_window = ctk.CTkToplevel(app)
    scores_window.title("High Scores")
    scores_window.geometry("300x400")

    scores_frame = ctk.CTkFrame(master=scores_window)
    scores_frame.pack(pady=20, padx=20, fill="both", expand=True)

    scores_label = ctk.CTkLabel(master=scores_frame, text=f"Scores:\n{scores_text}", anchor="w", font=("Arial", 14))
    scores_label.pack(side="left", fill="both", expand=True)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Flappy Bird Menu")
app.geometry("400x400")

frame = ctk.CTkFrame(master=app)
frame.pack(pady=50, padx=60, fill="both", expand=True)

nickname_label = ctk.CTkLabel(master=frame, text="Enter Nickname:", font=("Arial", 16))
nickname_label.pack(pady=10)

nickname_entry = ctk.CTkEntry(master=frame, font=("Arial", 16))
nickname_entry.pack(pady=10)

#nickname gereksinimi
def nck_name():
    nickname = nickname_entry.get()
    if nickname:
        threading.Thread(target=launch_game, args=(nickname,)).start()
    else:
        error_label = ctk.CTkLabel(master=frame, text="Please enter a nickname!", font=("Arial", 12, "bold"), text_color="red")
        error_label.pack()

start_button = ctk.CTkButton(master=frame, text="Start Game", command=nck_name)
start_button.pack(pady=12)

show_scores_button = ctk.CTkButton(master=frame, text="Show Scores", command=show_scores_window)
show_scores_button.pack(pady=12)

exit_button = ctk.CTkButton(master=frame, text="Exit", command=app.destroy)
exit_button.pack(pady=12)

create_database()
app.mainloop()

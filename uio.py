import pygame
import random
import os
import sys
 
"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
""" 
 
pygame.font.init()
pygame.init() #initialize pygame
 
# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per blo ck
block_size = 30
score = 0
high_score = 0
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
screen = pygame.display.set_mode((640, 480))

   
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")

# SHAPE FORMATS
 
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]
 
Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]
 
I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]
 
O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]
 
J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]
 
L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]
 
T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]
 
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape

def create_piece(column, row, shape):
    color = shape_colors[shapes.index(shape)]
    return {
        'x': column,
        'y': row,
        'shape': shape,
        'color': color,
        'rotation': 0
    }

def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]
 
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid
 
 
def convert_shape_format(piece):
    positions = []
    format = piece['shape'][piece['rotation'] % len(piece['shape'])]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece['x'] + j, piece['y'] + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions
 
def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)
 
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
 
    return True
 
 
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False
 
 
def get_shape():
    global shapes, shape_colors
    return create_piece(5, 0, random.choice(shapes)) 
 
def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
 
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))
 
 
def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + play_width, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))  # vertical lines
 
 
def clear_rows(grid, locked):
    global score
    # need to see if row is clear the shift every other row above down one
 
    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
            score += inc * 10



def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))
    
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    # Clear the area where the next shape is being drawn
    pygame.draw.rect(surface, BLACK, (sx, sy - 30, 150, 200))

    surface.blit(label, (sx + 10, sy - 30))

    format = piece['shape'][piece['rotation'] % len(piece['shape'])]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece['color'], (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)


def draw_window(surface, grid, score, high_score, username):
    surface.fill((0,0,0))
    # Tetris Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255,255,255))
 
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))
 
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 0)
 
    # draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)
    # pygame.display.update()

    draw_score(surface, score)
    #display the score

    draw_high_score(surface, high_score)
    #display the high score

    draw_username(surface, username)
    # Display the username

def draw_score(surface, score):
    font=pygame.font.SysFont('comicsans',30)
    label=font.render('score:' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy=top_left_y + play_height / 2 - 100
    surface.blit(label,(sx + 20,sy + 160))

def draw_high_score(surface, high_score):
    font = pygame.font.SysFont('comicsans', 20)
    high_score_label = font.render('High Score: ' + str(high_score), 1, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    surface.blit(high_score_label, (sx + 20, sy + 200))

def save_high_score(username, high_score):
    try:
        with open("highscore.txt", "a") as file:  # Change mode to "w"
            file.write(f"Username: {username}, High Score: {high_score}\n")
        print("High score saved successfully!")
    except Exception as e:
        print("An error occurred while saving the high score:", e)


def load_high_score():
    try:
        with open("highscore.txt", "r") as file:
            lines = file.readlines()
            if lines:
                for line in reversed(lines):
                    if line.startswith("Username:"):
                        parts = line.split(",")
                        prev_high_score = int(parts[-1].strip().split(":")[-1])
                        return prev_high_score
            else:
                print("High score file is empty. Using default high score of 0.")
                return 0
    except Exception as e:
        print("An error occurred while loading the high score:", e)
        print("Using default high score of 0.")
        return 0

def read_high_scores(file_path):
    high_scores = []
    with open("highscore.txt", 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                username = parts[0].split(':')[1].strip()
                score = int(parts[1].split(':')[1].strip())
                high_scores.append((username, score))
    return high_scores

# Function to display text on the window
def display_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    window.blit(text_surface, text_rect)

def draw_username(surface, username):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Player: ', 1, (255, 255, 255))
    label_width, label_height = label.get_size()
    username_label = font.render(username, 1, (255, 255, 255))
    username_width, username_height = username_label.get_size()
    
    sx = s_width - (top_left_x + play_width + 50 + label_width + 20)
    sy = top_left_y + play_height / 2 - 100 + label_height + username_height + 10
    # Position below label with a small gap
    
    surface.blit(label, (sx, sy - label_height))  # Render label
    surface.blit(username_label, (sx + label_width - 90, sy))  # Render username

def save_username(username, score):
    try:
        with open("user_scores.txt", "a") as file:
            file.write(f"Username: {username}, Score: {score}\n")
        print("Username and score saved successfully!")
    except Exception as e:
        print("An error occurred while saving the username and score:", e)

def main(username, high_score):
    global grid, score, window

   
    locked_positions = {}  # (x,y):(255,0,0)
    grid = create_grid(locked_positions)
 
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    score = 0 #reset score
 
    while run:
        fall_speed = 0.27
 
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
 
        # PIECE FALLING CODE
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece['y'] += 1
            if not (valid_space(current_piece, grid)) and current_piece['y'] > 0:
                current_piece['y'] -= 1
                change_piece = True
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece['x'] -= 1
                    if not valid_space(current_piece, grid):
                        current_piece['x'] += 1
 
                elif event.key == pygame.K_RIGHT:
                    current_piece['x'] += 1
                    if not valid_space(current_piece, grid):
                        current_piece['x'] -= 1
                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece['rotation'] = (current_piece['rotation'] + 1) % len(current_piece['shape'])
                    if not valid_space(current_piece, grid):
                        current_piece['rotation'] = (current_piece['rotation'] + 1) % len(current_piece['shape'])
 
                if event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece['y'] += 1
                    if not valid_space(current_piece, grid):
                        current_piece['y'] -= 1
 
                if event.key == pygame.K_SPACE:
                   while valid_space(current_piece, grid):
                       current_piece['y'] += 1
                   current_piece['y'] -= 1
                   print(convert_shape_format(current_piece))  # todo fix
 
        shape_pos = convert_shape_format(current_piece)
 
        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = shape_colors[shapes.index(current_piece['shape'])]
 
        # IF PIECE HIT GROUND
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = shape_colors[shapes.index(current_piece['shape'])]
            current_piece = create_piece(5, 0, random.choice(shapes))
            next_piece = create_piece(5, 0, random.choice(shapes))
            change_piece = False
 
            # call four times to check for multiple clear rows
            clear_rows(grid, locked_positions)

            #increase score for clearing rows
            score += 10 #add appropriate scoring logic here

            
        draw_window(window, grid, score, high_score, username)
        draw_next_shape(next_piece, window)
        pygame.display.update()

 
        # Check if user lost
        if check_lost(locked_positions):
            run = False
            
    if score > high_score:
            high_score = score
            save_high_score(username, high_score)  #save the new high score
        # Save the score whenever it changes
    save_username(username,score)  # Save username along with the score

    draw_text_middle("You Lost", 40, (255,255,255), win)
    pygame.display.update()
    pygame.time.delay(2000)

     # Display the high scores at the end of the game
    high_scores = read_high_scores('highscore.txt')
    display_high_scores(high_scores)

    pygame.time.delay(7000)

def display_high_scores(high_scores):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Scoreboard', 1, (255, 255, 255))  # Render the label
    label_rect = label.get_rect(center=(screen.get_width() // 2, 50))  # Center the label horizontally at the top
    screen.blit(label, label_rect)  # Display the label
    
    # Get the last 10 high scores with usernames
    last_10_scores = high_scores[-10:]
    
    # Calculate the starting y-coordinate for the scores
    y_offset = (screen.get_height() - (len(last_10_scores) * 40)) // 2
    
    for idx, (username, score) in enumerate(last_10_scores, start=1):
        text = f"{idx}. {username}: {score}"
        rendered_text = font.render(text, True, (255, 255, 255))
        text_rect = rendered_text.get_rect(center=(screen.get_width() // 2, y_offset))
        screen.blit(rendered_text, text_rect)
        y_offset += 40
    
    pygame.display.flip()

def main_menu():
    run = True
    username = get_username()  # Get the username before starting the game
    high_score = load_high_score()  # Load the high scor
    while run:
        win.fill((0,0,0))
        draw_text_middle('Press any key to begin.', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
 
            if event.type == pygame.KEYDOWN:
                main(username, high_score)
    pygame.quit()

win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
 
def get_username():
    font = pygame.font.SysFont('comicsans', 60)
    title_label = font.render('TETRIS', 1, (255,255,255))
    win.blit(title_label, (top_left_x + play_width / 2 - (title_label.get_width() / 2), 30))

    input_box = pygame.Rect(s_width // 2 - 100, s_height // 2 - 12, 200, 24)
    font = pygame.font.SysFont('comicsans', 30)
    input_label = font.render('Enter your name:', 1, (255, 255, 255))
    username = ''
    active = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return username
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode

        # Clear the screen
        win.fill(BLACK)

        # Render the input box and text
        pygame.draw.rect(win, WHITE, input_box, 2)
        win.blit(input_label, (s_width // 2 - input_label.get_width() // 2, s_height // 2 - input_label.get_height() - 20))
        display_text(username, 20, s_width // 2, s_height // 2)

        # Update the display
        pygame.display.update()

if __name__ == "__main__":
    main_menu()  # start game

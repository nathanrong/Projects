import pygame
import random

pygame.init()

# Establish Window Size and Game Constants
window_width = 1020
window_height = 920
rows = 6
columns = 5
padding = window_width * 0.01
margin = padding * 2
box_size = window_width * 0.08
letter_size = window_width * 0.06

# Game Colors
color_black = (0, 0, 0)
color_lblack = (43, 40, 39)
color_white = (255, 255, 255)
color_green = (131, 234, 139)
color_dgray = (150, 150, 150)
color_gray = (200, 200, 200)
color_lgray = (211, 211, 211)
color_yellow = (233, 244, 97)
color_blue = (172, 225, 242)

# Load Game Data
from WordleAnswers import wordle_answers_December_15_2024
from WordleAcceptableAnswers import wordle_acceptable_answers
game_message = ["Genius", "Impressive", "Magnificent", "Splendid", "Great", "Phew"]

# Game Variables
target_word = wordle_answers_December_15_2024[random.randint(1, len(wordle_answers_December_15_2024))].upper()
print("The Word is: " + target_word)
guess = ""
guesses = [ [""] * columns for _ in range(rows)]
feedback = [[None] * columns for _ in range(rows)]
green_letters, yellow_letters, gray_letters = [], [], []
game_finish = False

# Game Calculations
# Create width/height of all boxes
grid_width = columns * box_size + (columns - 1) * padding
grid_height = rows * box_size + (rows - 1) * padding
title_width = window_width * 0.80
title_height = window_height * 0.08
letters_width = (window_width * 0.75) / 10
game_message_width = window_width * 0.14
game_message_height = window_height * 0.04 
# Find center locations of all objects
center_x = (window_width - grid_width) / 2
center_y = margin + title_height + padding * 2
center_x_title = (window_width - title_width) / 2
line_y = margin + title_height + padding
center_x_message = (window_width - game_message_width) / 2
# Calculate Spacing between letters -> temporary fix to regions not fitting on screen
available_height = window_height - (title_height + grid_height + margin + 2 * padding)
alphabet_row_height = available_height / 3.5

# Pygame Setup and Font Types and Letter/Symbol Loading
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Wordle ~~ Yay!~~')
font_title = pygame.font.Font('Helvetica-Bold.ttf', int(title_height * 0.90))
font_buttons = pygame.font.Font('Helvetica-Bold.ttf', int(box_size * 0.25))
font_message = pygame.font.Font('Helvetica.ttf', int(box_size * 0.25))
alphabet_rows = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'], 
                 ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'], 
                 ['Z', 'X', 'C', 'V', 'B', 'N', 'M' ]]
backspace_icon = pygame.image.load('backspace.png')
backspace_icon = pygame.transform.scale(backspace_icon, (box_size * 0.6, box_size * 0.6))

# Helper Functions
def draw_button(x, y, text, color, size_type, radius = 3):
    button_rect = pygame.Rect(x, y, size_type, size_type)
    pygame.draw.rect(screen, color, (x, y, size_type, size_type), border_radius = radius)
    text_surface = font_buttons.render(text, True, color_black)
    text_rect = text_surface.get_frect(center=(x + size_type / 2, y + size_type / 2))
    screen.blit(text_surface, text_rect)
    return button_rect

def check_guess(target_word, row):
    global guess
    target_word_letters = {letter: target_word.count(letter) for letter in set(target_word)}
    for i in range(len(guess)):
        if guess[i] == target_word[i] and target_word_letters[guess[i]] > 0:
            feedback[row][i] = color_green
            if guess[i] not in green_letters:
                green_letters.append(guess[i])
            target_word_letters[guess[i]] -= 1
        elif guess[i] in target_word and target_word_letters[guess[i]] > 0:
            feedback[row][i] = color_yellow
            if guess[i] not in yellow_letters:
                yellow_letters.append(guess[i])
            target_word_letters[guess[i]] -= 1
        elif guess[i] not in target_word or target_word_letters[guess[i]] == 0:
            feedback[row][i] = color_dgray
            if guess[i] not in gray_letters:
                gray_letters.append(guess[i])
    return feedback

def game_logic(green_count, yellow_count, row):
    global game_finish
    game_finish = False
    if guess == target_word:
        # Display ending message, and end the game
        game_finish = True
        pygame.draw.rect(screen, color_lblack, (center_x_message, window_height * 0.30, game_message_width, game_message_height), border_radius = 3)
        text_surface = font_message.render(game_message[row], True, color_white)
        text_rect = text_surface.get_frect(center=(center_x_message + game_message_width / 2, window_height * 0.30 + game_message_height / 2))
        screen.blit(text_surface, text_rect)
    elif guess != target_word and row == rows - 1:
        game_finish = True
        if len(green_count)> 2:
            loss_message = "Close"
        else:
            loss_message = "Not Quite"
        
        pygame.draw.rect(screen, color_lblack, (center_x_message, window_height * 0.30, game_message_width, game_message_height), border_radius = 3)
        text_surface = font_message.render(loss_message, True, color_white)
        text_rect = text_surface.get_frect(center=(center_x_message + game_message_width / 2, window_height * 0.30 + game_message_height / 2))
        screen.blit(text_surface, text_rect)

# White background, Title, and Divider
screen.fill(color_white)
pygame.draw.rect(screen, color_blue, (center_x_title, margin, title_width, title_height))
text_surface = font_title.render("Wordle", True, (0, 0, 0))
text_rect = text_surface.get_frect(center=(center_x_title + title_width / 2, padding + margin + title_height / 2))
screen.blit(text_surface, text_rect)
pygame.draw.line(screen, color_lgray, ((window_width - 0.9 * window_width), line_y), (0.9 * window_width, line_y), 2)

# Draw Guess Box
for row in range(rows):
    for col in range(columns):
         x = center_x + col * (box_size + padding)
         y = center_y + row * (box_size + padding)
         pygame.draw.rect(screen, color_gray, (x, y, box_size, box_size), 2)

# Main Loop
running = True
current_row = 0
current_col = 0

pygame.display.update()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse click handling
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_finish:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if a letter key was clicked
            start_y = center_y + rows * (box_size + padding) + padding
            for row_idx, row in enumerate(alphabet_rows):
                start_x = (window_width - len(row) * (letter_size + padding)) / 2
                for col_idx, letter in enumerate(row):
                    x = start_x + col_idx * (letter_size + padding)
                    y = start_y + row_idx * alphabet_row_height
                    key_rect = pygame.Rect(x, y, letter_size, letter_size)

                    if key_rect.collidepoint(mouse_x, mouse_y):
                        if current_col < columns:
                            guesses[current_row][current_col] = letter
                            # Draw the guessed letter in the grid
                            x = center_x + current_col * (box_size + padding)
                            y = center_y + current_row * (box_size + padding)
                            pygame.draw.rect(screen, color_black, (x, y, box_size, box_size), 2)
                            letter_guessed_surface = font_buttons.render(letter, True, color_black)
                            letter_guessed_rect = letter_guessed_surface.get_frect(center=(x + box_size / 2, y + box_size / 2))
                            screen.blit(letter_guessed_surface, letter_guessed_rect)
                            current_col += 1

            # Check if the backspace button was clicked
            button_y = start_y + 2 * alphabet_row_height - padding / 2
            backspace_x = start_x + len(alphabet_rows[2]) * (letter_size + padding)
            backspace_rect = pygame.Rect(backspace_x, button_y, box_size, box_size)

            if backspace_rect.collidepoint(mouse_x, mouse_y):
                if current_col > 0:
                    current_col -= 1
                    guesses[current_row][current_col] = ""
                    # Clear the grid letter
                    x = center_x + current_col * (box_size + padding)
                    y = center_y + current_row * (box_size + padding)
                    pygame.draw.rect(screen, color_white, (x, y, box_size, box_size))
                    pygame.draw.rect(screen, color_gray, (x, y, box_size, box_size), 2)

            # Check if the enter button was clicked
            enter_x = start_x - letter_size - padding * 3
            enter_rect = pygame.Rect(enter_x, button_y, box_size, box_size)

            if enter_rect.collidepoint(mouse_x, mouse_y):
                if current_col == columns:
                    guess = "".join(guesses[current_row])
                    if guess.lower() in wordle_acceptable_answers:
                        feedback = check_guess(target_word, current_row)
                        y = center_y + current_row * (box_size + padding)
                        for col in range(columns):
                            x = center_x + col * (box_size + padding)
                            letter = guesses[current_row][col]
                            feedback_color = feedback[current_row][col]
                            pygame.draw.rect(screen, feedback_color, (x, y, box_size, box_size))

                            # Redraw the guessed word
                            letter_guessed_surface = font_buttons.render(guesses[current_row][col], True, color_white)
                            letter_guessed_rect = letter_guessed_surface.get_frect(center=(x + box_size / 2, y + box_size / 2))
                            screen.blit(letter_guessed_surface, letter_guessed_rect)

                        game_logic(green_letters, yellow_letters, current_row)

                        if current_row == rows - 1:
                            game_finish = True
                        else:
                            current_row += 1
                            current_col = 0
                    else:
                        pass
                else:
                    pass

        # Keyboard click handling
        if event.type == pygame.KEYDOWN and game_finish == False:
            # Check if backspace key is hit
            if event.key == pygame.K_BACKSPACE:
                if current_col > 0:
                    current_col -= 1
                    guesses[current_row][current_col] = ""
                    x = center_x + current_col * (box_size + padding)
                    y = center_y + current_row * (box_size + padding)
                    pygame.draw.rect(screen, color_white, (x, y, box_size, box_size))
                    pygame.draw.rect(screen, color_gray, (x, y, box_size, box_size), 2)
            # Check if enter key is hit
            elif event.key == pygame.K_RETURN:
                if current_col == columns:
                    guess = "".join(guesses[current_row])
                    if guess.lower() in wordle_acceptable_answers:
                        feedback = check_guess(target_word, current_row)
                        y = center_y + current_row * (box_size + padding)
                        
                        for col in range(columns):
                            x = center_x + col * (box_size + padding)
                            letter = guesses[current_row][col]
                            feedback_color = feedback[current_row][col]
                            pygame.draw.rect(screen, feedback_color, (x, y, box_size, box_size))

                            # Redraw the guessed word
                            letter_guessed_surface = font_buttons.render(guesses[current_row][col], True, color_white)
                            letter_guessed_rect = letter_guessed_surface.get_frect(center = (x + box_size / 2, y + box_size / 2))
                            screen.blit(letter_guessed_surface, letter_guessed_rect)

                        game_logic(green_letters, yellow_letters, current_row)

                        if current_row == rows - 1:
                            game_finish = True
                            pass
                        else:
                            current_row += 1
                            current_col = 0
                    else:
                        pass
                else:
                     pass

            # Check if letter keys are hit
            elif pygame.K_a <= event.key <= pygame.K_z:
                if current_row == rows - 1 and current_col == columns:
                    pass
                else:
                    if current_col < columns:
                        letter_guessed = chr(event.key).upper()
                        guesses[current_row][current_col] = letter_guessed
                        x = center_x + current_col * (box_size + padding)
                        y = center_y + current_row * (box_size + padding)
                        pygame.draw.rect(screen, color_black, (x, y, box_size, box_size), 2)
                        for col in range(columns):
                                    x = center_x + col * (box_size + padding)
                                    letter_guessed_surface = font_buttons.render(guesses[current_row][col], True, color_black)
                                    letter_guessed_rect = letter_guessed_surface.get_frect(center = (x + box_size / 2, y + box_size / 2))
                                    screen.blit(letter_guessed_surface, letter_guessed_rect)
                        current_col += 1
            


    # Draw alphabet below word bank
    start_y = center_y + rows * (box_size + padding) + padding
    for row_idx, row in enumerate(alphabet_rows):
        start_x = (window_width - len(row) * (letter_size + padding)) / 2
        for col_idx, letter in enumerate(row):
            x = start_x + col_idx * (letter_size + padding)
            y = start_y + row_idx * alphabet_row_height
            # Recolor word bank to reflect guesses
            if letter in green_letters:
                color = color_green
            elif letter in yellow_letters:
                color = color_yellow
            elif letter in gray_letters:
                color = color_dgray
            else:
                color = color_lgray

            draw_button(x, y, letter, color, letter_size)


    # Calculate center for enter and backspace button
    button_y = start_y + 2 * alphabet_row_height - padding / 2
    enter_x = start_x - letter_size - padding * 3
    backspace_x = start_x + len(alphabet_rows[2]) * (letter_size + padding)

    icon_x = backspace_x + (box_size - backspace_icon.get_width()) / 2
    icon_y = button_y + (box_size - backspace_icon.get_height()) / 2

    # Insert enter and backspace buttons
    draw_button(enter_x, button_y, "ENTER", color_gray, box_size)
    pygame.draw.rect(screen, color_gray, (backspace_x, button_y, box_size, box_size), border_radius = 3)
    screen.blit(backspace_icon, (icon_x, icon_y))



    pygame.display.update()

pygame.quit()
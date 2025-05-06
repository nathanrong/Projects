import pygame

pygame.init()
window_width = 720
pixelwidth = window_width // 3
screen = pygame.display.set_mode((window_width,window_width))
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 48)
announcement = font.render('', True, 'green')
textrect = announcement.get_rect()
textrect.center = (window_width // 2 - pixelwidth // 1.5, window_width // 2)
running = True

board = [
    [None, None, None],
    [None, None, None],
    [None, None, None]
]

player1 = 0
player2 = 1
currentplayer = player1
breakout = False
    
def load_icon(path, resolution):
    icon = pygame.image.load(path)
    return pygame.transform.scale(icon, resolution)

icon_x = load_icon('xfile.png',[pixelwidth, pixelwidth])
icon_o = load_icon('ofile.png',[pixelwidth, pixelwidth ])
grid = load_icon('grid.png',[window_width, window_width])

def player_turn(player, breakout):
    if breakout:
        pass
    else:
        player_coord = pygame.math.Vector2(pygame.mouse.get_pos())
        normal_coord = player_coord // pixelwidth
        if pygame.mouse.get_pressed()[0]:
            col, row = map(int, normal_coord)
            if board[row][col] == None:
                board[row][col] = player
                global currentplayer
                currentplayer = 1 - currentplayer

def draw_icon():
    for i, row in enumerate(board):
        for j, col in enumerate(board):
            if board[i][j] == 0:
                screen.blit(icon_x, (j * pixelwidth, i * pixelwidth))
            if board[i][j] == 1:
                screen.blit(icon_o, (j * pixelwidth, i * pixelwidth))

def equal_icon(elements, player):
    for element in elements:
        if element != player:
            return False
    return True

def has_winning_row(player):
    return equal_icon(board[0], player) \
        or equal_icon(board[1], player) \
        or equal_icon(board[2], player)

def has_winning_col(player):
    return equal_icon([board[0][0], board[1][0], board[2][0]], player) \
        or equal_icon([board[0][1], board[1][1], board[2][1]], player) \
        or equal_icon([board[0][2], board[1][2], board[2][2]], player)

def has_winning_dia(player):
    return equal_icon([board[0][0], board[1][1], board[2][2]], player) \
        or equal_icon([board[0][2], board[1][1], board[2][0]], player)

def find_winner(player):
    return has_winning_row(player) \
        or has_winning_col(player) \
        or has_winning_dia(player)

def check_for_winner():
    global announcement
    if find_winner(player1):
        announcement = font.render('Player 1 WON!', True, 'green')
        return True
    if find_winner(player2):
        announcement = font.render('Player 2 WON!', True, 'green')
        return True

def check_for_no_win():
    if any(None in sub for sub in board):
        pass
    else:
        return True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    screen.fill("white")
    screen.blit(grid, (0,0))
    clock.tick(60)
    player_turn(currentplayer,breakout)
    pygame.event.wait()
    draw_icon()
    if check_for_winner():
        screen.blit(announcement, textrect)
        breakout = True
    if check_for_no_win():
        announcement = font.render('Nobody Wins!', True, 'green')
        screen.blit(announcement, textrect)

pygame.quit()
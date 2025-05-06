import serial, pygame, math, pandas as pd

mcu = serial.Serial(port='COM6', baudrate=9600, timeout=0.25)

pygame.init()

clock = pygame.time.Clock()

color_black = (0, 0, 0)
color_lblack = (105, 105, 105)
color_white = (255, 255, 255)
color_blue = (173, 216, 230)
color_gray = (16, 16, 16)
color_lgray = (211, 211, 211)
color_lred = (255, 127, 127)
font_title = pygame.font.Font('Oxanium-Bold.ttf', 50)
font_label = pygame.font.Font('Helvetica-Bold.ttf', 25)
font_label_S = pygame.font.Font('Helvetica-Bold.ttf', 20)
font_value = pygame.font.Font('Helvetica.ttf', 20)

# Dimensioning
window_width = 920
window_height = 780
rows, columns = 1, 3
box_size = window_width * 0.25
padding = window_width * 0.01
margin = padding * 2
title_width = window_width * 0.80
title_height = window_height * 0.1
grid_width = columns * box_size + (columns - 1) * padding
grid_height = rows * box_size + (rows - 1) * padding
center_x = (window_width - grid_width) / 2
center_y = margin + title_height + padding * 2
center_x_title = (window_width - title_width) / 2
line_y = margin + title_height + padding * 2

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Avionics Lab Thrust Stand GUI')

running = True
screen.fill(color_blue)

# Function to draw GUI Framework
def draw_label(text, x, y, width, height, font, color=color_black):
    """
    Draw Box Headers

    Parameters
    ----------
    text : str
        Header
    x : float
        x location of header text box
    y : float
        y location of header text box
    width : float
        width of header text box
    height : float
        height of header text box
    font : var
        pygame Font type
    """
    label_height = height * 0.25
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_frect(center=(x + width / 2, y + label_height / 2))
    screen.blit(text_surface, text_rect)

def draw_data(value, x, y, width, height, color=color_black):
    """
    Draw Data in Boxes

    Parameters
    ----------
    value : str
        Data value
    x : float
        x location
    y : float
        y location
    width : float
        width of data text box
    height : float
        height of data text box
    color : hex
        Color hex
    """
    label_height = height * 0.25
    text_surface = font_value.render(str(value), True, color)
    text_rect = text_surface.get_rect(center=(x + width / 2, y + label_height + height * 0.25))  # 25% offset for label
    screen.blit(text_surface, text_rect)

def draw_button(x, y, width, height, label, value, font_label, bg_color=color_lred, border_radius=15):
    """
    Draw buttons and rect shape

    Parameters
    ----------
    x : float
        x location
    y : float
        y location
    width : float
        width of button
    height : float
        height of button
    label : str
        Header string
    value : str
        Data string
    bg_color : hex
        background color hex
    border_radius : int
        radius of button corners
    """
    pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=border_radius)
    draw_label(label, x, y, width, height, font_label)
    draw_data(value, x, y, width, height)

def draw_rpm_speedometer(x, y, radius, rpm_value):
    """
    Draw RPM speedometer to display RPM

    Parameters
    ----------
    x : float
        x location
    y : float
        y location
    radius : float
        radius of circle
    rpm_value : str
        RPM value to be displayed
    """
    max_rpm = 12000  # Adjust according to range of RPM values
    rpm_value = float(rpm_value)
    # Calculate the angle for the RPM needle (280 degrees rotation)
    rpm_angle = 130 + (rpm_value / max_rpm) * 280
    needle_angle = math.radians(rpm_angle)
    
    # Draw the circular background for the speedometer
    pygame.draw.circle(screen, color_lblack, (x + radius, y + radius), radius)
    pygame.draw.circle(screen, color_gray, (x + radius, y + radius), radius, 5)
    
    # Draw RPM markers
    marker_offset = 20
    for i in range(6):
        angle = math.radians(220 + (i * 56) - 90)
        marker_x = x + radius + math.cos(angle) * (radius + marker_offset)
        marker_y = y + radius + math.sin(angle) * (radius + marker_offset)
        pygame.draw.circle(screen, color_lblack, (int(marker_x), int(marker_y)), 5)
        draw_label(f'{int(i * 20 * max_rpm / 100)}', marker_x - 15, marker_y - 15, 30, 30, font_value, color_black)

    # Draw the RPM needle
    needle_x = x + radius + math.cos(needle_angle) * (radius - 10)
    needle_y = y + radius + math.sin(needle_angle) * (radius - 10)
    pygame.draw.line(screen, color_black, (x + radius, y + radius), (needle_x, needle_y), 3)
    arrow_size = 20
    arrow_angle = needle_angle + math.pi
    arrow_x1 = needle_x + math.cos(arrow_angle + math.radians(30)) * arrow_size
    arrow_y1 = needle_y + math.sin(arrow_angle + math.radians(30)) * arrow_size
    arrow_x2 = needle_x + math.cos(arrow_angle - math.radians(30)) * arrow_size
    arrow_y2 = needle_y + math.sin(arrow_angle - math.radians(30)) * arrow_size
    pygame.draw.polygon(screen, color_black, [(needle_x, needle_y), (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)])

    # Draw the current RPM value in the center of the dial
    draw_label(f'{int(rpm_value)} RPM', x + radius - 40, y + radius - 25 + box_size*0.2, 80, 50, font_label_S, color_white)

def scale_to_fit(img, max_dim):
    """
    Image scaling helper function

    Parameters
    ----------
    img : pygame.image
        image loaded in pygame
    max_dim : float
        larger dimension (width or height) to scale down

    Returns
    ----------
    image : pygame.image
        scaled image version
    """
    width, height = img.get_size()
    scale = max_dim / max(width, height)
    new_size = (int(width * scale), int(height * scale))
    return pygame.transform.scale(img, new_size)

class DataLog:
    """
    Class supporting data logging using pandas dataframe

    Attributes
    ----------
    columns : list
        column headers
    data : list
        list of data values, stored in pandas dataframe
    """
    def __init__(self):
        self.columns = ['Time (s)', 'Thrust (gF)', 'RPM', 'Advance Ratio', 'Power (W)',
                        'Voltage (V)', 'Current (A)', 'Throttle (%)', 'Wind Speed (in/s)']
        self.data = []

    def log(self, time, thrust, rpm, advr, power, voltage, current, throttle, windspeed):
        self.data.append([
            time, thrust, rpm, advr, power, voltage, current, throttle, windspeed
        ])

    def save_to_csv(self, filename='thrust_data.csv'):
        pd.DataFrame(self.data, columns=self.columns).to_csv(filename, index=False)

# Function to load GUI frame
def load_frame(time=0, Thrust=0, Windspeed=0, RPM=0, ADVR=0, Power=0, Voltage=0, Current=0, Throttle=0):
    """
    Loads all design elements in GUI

    Parameters
    ----------
    time : float
        time value
    Thrust : float
        thrust value
    Windspeed : float
        windspeed value
    RPM : float
        RPM value
    ADVR : float
        Advance ratio value
    Power : float
        power value
    Voltage : float
        voltage value
    Current : float
        current value
    Throttle : int
        Throttle value

    Returns
    ----------
    power_rect : pygame.rect
        Interactable rect of power button
    log_rect : pygame.rect
        Interactable rect of log button
    throttle_rect : pygame.rect
        Interactable rect of throttle button
    """
    # Fill background
    screen.fill(color_blue)

    # Title Box
    pygame.draw.rect(screen, color_white, (center_x_title, margin, title_width, title_height), border_radius=15)
    text_surface = font_title.render('Thrust Stand GUI', True, color_black)
    text_rect = text_surface.get_rect(center=(center_x_title + title_width / 2, margin * 1.5 + title_height / 2))
    screen.blit(text_surface, text_rect)

    # Separator Line
    pygame.draw.line(screen, color_gray, (0.1 * window_width, line_y), (0.9 * window_width, line_y), 2)

    # Top Row
    top_y = center_y + padding * 2
    labels_top = ['RPM', 'Thrust', 'Advance Ratio']
    for i in range(3):
        x = center_x + i * (box_size + padding)
        pygame.draw.rect(screen, color_lgray, (x, top_y, box_size, box_size), border_radius=15)
        draw_label(labels_top[i], x, top_y, box_size, box_size, font_label)

    advr_x = center_x + 2 * (box_size + padding)

    adv_ratio_img_rect = plane_img.get_rect(center=(advr_x + box_size / 2, top_y + box_size / 2))
    screen.blit(plane_img, adv_ratio_img_rect)
    draw_data(f'{ADVR}', advr_x, top_y, box_size, box_size * 1.6)


    # Draw Thrust Bar
    try:
        thrust_val = float(Thrust)
    except:
        thrust_val = 0

    thrust_ratio = min(max(thrust_val / max_thrust, 0), 1)

    # Bar dimensions
    bar_margin = 10
    bar_height = 150
    bar_width = box_size - 2 * bar_margin
    bar_x = center_x + box_size + padding + bar_margin
    bar_y = top_y + box_size - bar_margin - bar_height

    # Draw empty bar
    pygame.draw.rect(screen, color_white, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
    # Draw filled portion in green
    filled_width = int(bar_width * thrust_ratio)
    pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, filled_width, bar_height), border_radius=5)
    draw_data(f'{Thrust} gF', center_x + box_size + padding, top_y, box_size, box_size / 2)

    # Draw the RPM speedometer in the RPM box
    rpm_box_radius = box_size * 0.35
    draw_rpm_speedometer(center_x + rpm_box_radius / 2, top_y + (box_size * 0.35) - rpm_box_radius / 2 + padding*2, rpm_box_radius, rpm_value=RPM)

    # Middle Row
    middle_y = top_y + box_size + padding * 1.5
    small_box_height = (box_size - padding) / 2

    # Column 1: Two stacked boxes
    pygame.draw.rect(screen, color_lgray, (center_x, middle_y, box_size, small_box_height), border_radius=15)
    draw_label('Throttle Percent', center_x, middle_y, box_size, small_box_height, font_label_S)
    draw_data(f'{Throttle}%', center_x, middle_y, box_size, small_box_height)

    # User Throttle Input
    global input_rect
    input_height = small_box_height * 0.5
    input_width = box_size
    input_rect = pygame.Rect(center_x + (box_size - input_width) / 2, middle_y + small_box_height + padding, input_width, input_height)
    pygame.draw.rect(screen, color_white, input_rect, border_radius=10)

    # Render user input text
    text_surface = font_value.render(user_throttle_input, True, color_black)
    screen.blit(text_surface, (input_rect.x + 100, input_rect.y + input_height / 4))

    # Throttle Button
    button_height = small_box_height * 0.5
    y_b5 = middle_y + small_box_height + input_height - (button_height - small_box_height) / 2 - padding
    draw_button(center_x, y_b5, box_size, button_height, 'Throttle Push', 'Press to Rearm' if throttling else 'Push Throttle', font_label_S)

    # Column 2: Two stacked boxes
    x_col2 = center_x + box_size + padding
    pygame.draw.rect(screen, color_lgray, (x_col2, middle_y, box_size, small_box_height), border_radius=15)
    draw_label('Power', x_col2, middle_y, box_size, small_box_height, font_label_S)
    draw_data(f'{Power} W', x_col2, middle_y, box_size, small_box_height)
    draw_data('P = IV', x_col2, middle_y, box_size, small_box_height * 1.6)

    y_b6 = middle_y + small_box_height + padding
    pygame.draw.rect(screen, color_lgray, (x_col2, y_b6, box_size, small_box_height), border_radius=15)
    draw_label('Current / Voltage', x_col2, y_b6, box_size, small_box_height, font_label_S)
    draw_data(f'{Current} A', x_col2, y_b6, box_size, small_box_height)
    draw_data(f'{Voltage} V', x_col2, y_b6, box_size, small_box_height * 1.5)


    # Column 3: Regular box
    for i in range(1, 2):  # Only one box for this column
        x = center_x + i * (box_size + padding) + box_size + padding
        pygame.draw.rect(screen, color_lgray, (x, middle_y, box_size, box_size), border_radius=15)
        draw_label('Wind Speed', x, middle_y, box_size, box_size, font_label)
        draw_data(f'{Windspeed} in/s', x, middle_y, box_size, box_size*1.75)
        
    windspeed_x = center_x + box_size + padding + box_size + padding
    windspeed_img_rect = windspeed_img.get_rect(center=(windspeed_x + box_size / 2, middle_y + box_size / 2))
    screen.blit(windspeed_img, windspeed_img_rect)

    # Bottom Row
    bottom_y = middle_y + box_size + padding * 2
    button_height = window_height * 0.15
    total_width = window_width * 0.8
    box_a_width = total_width * 0.35
    box_b_width = total_width * 0.35
    box_c_width = total_width * 0.25
    total_combined_width = box_a_width + box_b_width + box_c_width + 2 * padding
    start_x = (window_width - total_combined_width) / 2

    x_log = start_x + box_a_width + padding
    # Create button rects
    power_rect = pygame.Rect(start_x, bottom_y, box_a_width, button_height)
    log_rect = pygame.Rect(x_log, bottom_y, box_b_width, button_height)
    throttle_rect = pygame.Rect(center_x, y_b5, box_size, small_box_height)
    # Draw Power and Log Buttons
    draw_button(start_x, bottom_y, box_a_width, button_height, 'Power Button', 'ON' if power_on else 'OFF', font_label_S)
    draw_button(x_log, bottom_y, box_b_width, button_height, 'Log Button', 'Log Data' if log_on else 'Arm Data Logger', font_label_S)

    # Time
    x_time = x_log + box_b_width + padding
    pygame.draw.rect(screen, color_lgray, (x_time, bottom_y, box_c_width, button_height), border_radius=15)
    draw_label('Time (sec)', x_time, bottom_y, box_c_width, button_height, font_label_S)
    draw_data(time, x_time, bottom_y, box_c_width, button_height)

    return power_rect, log_rect, throttle_rect

# Loop Intialization Values
max_thrust = 800 # in grams
windspeed_img = pygame.image.load('wind-icon.png')
windspeed_img = scale_to_fit(windspeed_img, box_size * 0.6)
plane_img = pygame.image.load('plane-img.png')
plane_img = scale_to_fit(plane_img, box_size * 0.8)
power_on, log_on, throttling = False, True, False
time_start, throttle, user_throttle_input = 0, 0, ''
input_active, input_rect = False, None
power_rect, log_rect, throt_rect = load_frame()
logger = DataLog()

while running:
    # Framerate
    clock.tick(15)
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pos = (mouse_x, mouse_y)
            input_active = input_rect.collidepoint(mouse_pos)

            if power_rect.collidepoint(mouse_pos):
                power_on = not power_on
                time_start = pygame.time.get_ticks()

            elif log_rect.collidepoint(mouse_pos):
                log_on = not log_on
                if log_on == False:
                    logger.save_to_csv('session_data.csv')
                    print('Logging...')
            
            elif throt_rect.collidepoint(mouse_pos):
                throttling = not throttling
                if throttling and user_throttle_input != '':
                    throttle = str(min(max(int(user_throttle_input), 0), 100))
                    user_throttle_input = ''
                    # Send the throttle value to Arduino via serial
                    try:
                        if mcu.is_open and power_on:
                            mcu.write(f"[THROTCMD:{throttle}]\n".encode())
                            mcu.flush()
                    except:
                        print('COM Port not open')
        
        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_BACKSPACE:
                user_throttle_input = user_throttle_input[:-1]
            elif event.key == pygame.K_RETURN:
                input_active = False
            else:
                if len(user_throttle_input) < 3 and event.unicode.isdigit():
                    user_throttle_input += event.unicode

    thrust = windspeed = current = voltage = throttle = rpm = power = advr = '0'
    empty = True
    while empty and power_on:
        try:
            ser_out = mcu.readline()
            converted = str(ser_out, 'UTF-8')
            converted = converted.strip()
            if converted == '':
                continue
            else:
                if converted.startswith("<") and converted.endswith(">"):
                    data = converted[1:-1]
                    values = dict(item.split(":") for item in data.split(","))
                    print(values)
                    thrust = str(float(values['THRST']))
                    windspeed = str(float(values['WIND']))
                    current = str(float(values['CURR']))
                    voltage = str(float(values['VOLT']))
                    throttle = str(int(values['THROT']))
                    rpm = str(int(values['RPM']))
                    power = str(round(float(values['CURR']) * float(values['VOLT']), 1))
                    advr = str(round(60*float(values['WIND']) / (5.1*int(values['RPM'])), 1)) if int(values['RPM']) != 0 else '0'
                empty = False
        except:
            raise UserWarning('Data transfer unsuccessful')
    
    time = round((current_time - time_start)/1000, 2) if power_on else 0
    load_frame(time = time, Thrust = thrust, Windspeed = windspeed, RPM = rpm, Power = power, Voltage = voltage,
        Current = current, Throttle = throttle, ADVR = advr)

    if power_on and not empty:
        logger.log(time, thrust, rpm, advr, power, voltage, current, throttle, windspeed)
    
    pygame.display.update()
    
mcu.write(f"[THROTCMD:0]\n".encode())
mcu.close()
pygame.quit()
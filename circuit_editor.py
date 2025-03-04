""""
TODO :
    * select componants (remove the selected componants)
    * modify wires
    * add componants (resistor, capacitor, inductor, generator)
"""

import pygame as pg
from pygame.locals import *
import numpy as np


class Buttons:
    def __init__(self, type="wire", position=1):
        self.type = type
        self.selected = False
        self.VERTICAL_SPACING = 20
        self.WIDTH_RATIO = 0.8
        self.SIZE = np.array([TOOLBAR_WIDTH * self.WIDTH_RATIO, self.VERTICAL_SPACING*4])
        self.surf = pg.Surface(self.SIZE)
        self.rect = pg.Rect(((TOOLBAR_WIDTH-self.SIZE[0])/2, (self.VERTICAL_SPACING+self.SIZE[1])*position), self.SIZE)  # relative to the window
        self.update()

    
    def button_clicked(self):
        """
        This function is called every time the user clicks.
        It updates the buttons state (selected or not) --> update visual (calls update function)
        return the type of componant selected (or None if no componant is selected)
        """
        
        self.selected = not self.selected  # select/deselect componant clicked

        # deselect every componant when another is clicked
        for button in buttons:
            if self != button:
                button.selected = False
                button.update()

        # update visual
        self.update()

        # returns type if button selected
        if self.selected:
            return self.type
        return None

    def update(self):
        # draw button background
        self.surf.fill(RED)
        # draw button symbol (TODO)
        if self.type == "wire":
            draw_line_round_corners(self.surf, [0.1*self.rect.width, self.rect.height/2], [0.9*self.rect.width, self.rect.height/2], BLACK, WIRE_WIDTH)
        elif self.type == "resistor":
            pos1, pos2 = np.array([0.1*self.rect.width, self.rect.height/2]), np.array([0.9*self.rect.width, self.rect.height/2])
            draw_resistor(self.surf, pos1, pos2, BLACK)
        # draw button onto the toolbar
        toolbar.blit(self.surf, self.rect)
        # draw borders if selected
        if self.selected:
            pg.draw.rect(toolbar, DARK_BLUE, self.rect, WIRE_WIDTH)
        


def draw_resistor(surf, pos1, pos2, color):
    """
    blit a resistor onto the surface parameter
    """
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    # Use np.arctan2 to properly compute the angle
    alpha = np.arctan2(dy, dx)

    l = (np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2) - RESISTOR_WIDTH) / 2
    R_left, R_right = [pos1[0]+l*np.cos(alpha), pos1[1]+l*np.sin(alpha)], [pos1[0]+(l+RESISTOR_WIDTH)*np.cos(alpha), pos1[1]+(l+RESISTOR_WIDTH)*np.sin(alpha)]
    # branches
    draw_line_round_corners(surf, pos1, R_left, color, width=WIRE_WIDTH)
    draw_line_round_corners(surf, R_right, pos2, color, width=WIRE_WIDTH)
    # rectangle ABCD
    A = [R_left[0]-(RESISTOR_HEIGHT/2)*np.sin(alpha), R_left[1]+(RESISTOR_HEIGHT/2)*np.cos(alpha)]
    B = [R_left[0]+(RESISTOR_HEIGHT/2)*np.sin(alpha), R_left[1]-(RESISTOR_HEIGHT/2)*np.cos(alpha)]
    C = [R_right[0]+(RESISTOR_HEIGHT/2)*np.sin(alpha), R_right[1]-(RESISTOR_HEIGHT/2)*np.cos(alpha)]
    D = [R_right[0]-(RESISTOR_HEIGHT/2)*np.sin(alpha), R_right[1]+(RESISTOR_HEIGHT/2)*np.cos(alpha)]
    pg.draw.polygon(surf, color, [A,B,C,D], width=WIRE_WIDTH)


def draw_grid():
    """
    draw grid onto the display
    """
    for x in range(CELL_SIZE, CELL_SIZE*(GRID_SIZE[0]+1), CELL_SIZE):  # vertical lines
        pg.draw.line(display, DARK_GRAY, (x, 0), (x, display.get_height()), 1)
    for y in range(CELL_SIZE, CELL_SIZE*(GRID_SIZE[1]+1), CELL_SIZE):  # horizontal lines
        pg.draw.line(display, DARK_GRAY, (0, y), (display.get_width(), y), 1)


def draw_wires():
    """draw wires onto the display"""
    for wire in wires:
        draw_line_round_corners(display, wire[0]-np.array([TOOLBAR_WIDTH, 0]), wire[1]-np.array([TOOLBAR_WIDTH, 0]), BLUE, WIRE_WIDTH)


def draw_resistors():
    """draw resistors onto the display"""
    for resistor in resistors:
        draw_resistor(display, resistor[0]-np.array([TOOLBAR_WIDTH, 0]), resistor[1]-np.array([TOOLBAR_WIDTH, 0]), BLUE)


def snap_to_grid(coord):
    coord[1] = CELL_SIZE * round(coord[1] / CELL_SIZE)
    coord[0] = TOOLBAR_WIDTH + CELL_SIZE * round((coord[0] - TOOLBAR_WIDTH) / CELL_SIZE)
    return coord


def draw_line_round_corners(surf, start_pos, end_pos, color, width):
    pg.draw.line(surf, color, start_pos, end_pos, width)
    pg.draw.circle(surf, color, start_pos, width)  # add // 2 to get a simple rounded edge 
    pg.draw.circle(surf, color, end_pos, width)  # add // 2 to get a simple rounded edge 


def generate_tikz_code():
    """
    Génère le code TikZ pour les fils dessinés.
    """
    TIKZ_SCALE_FACTOR = 2
    # find the coordinate of the componant at the top left (used to simplify tikz code)
    offset = np.array(screen.get_size())
    for componant in (wires+resistors):
        offset[0] = min(offset[0], min(componant[0][0], componant[1][0])) 
        offset[1] = min(offset[1], min(componant[0][1], componant[1][1]))
    offset[0] = offset[0] - TOOLBAR_WIDTH
    offset = offset // CELL_SIZE  # convert to tikz coordinate

    # code
    tikz_code = "\\begin{tikzpicture}\n"
    
    for wire in wires:
        start = (wire[0] - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset
        end = (wire[1] - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset
        tikz_code += f"    \\draw ({start[0]*TIKZ_SCALE_FACTOR:.1f}, {-start[1]*TIKZ_SCALE_FACTOR:.1f}) -- ({end[0]*TIKZ_SCALE_FACTOR:.1f}, {-end[1]*TIKZ_SCALE_FACTOR:.1f});\n"
    for resistor in resistors:
        start = (resistor[0] - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset
        end = (resistor[1] - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset
        tikz_code += f"    \\draw ({start[0]*TIKZ_SCALE_FACTOR:.1f}, {-start[1]*TIKZ_SCALE_FACTOR:.1f}) to[R] ({end[0]*TIKZ_SCALE_FACTOR:.1f}, {-end[1]*TIKZ_SCALE_FACTOR:.1f});\n"
    
    tikz_code += "\\end{tikzpicture}"
    print(tikz_code)
    tikz_code = font.render(tikz_code, True, BLACK)
    return tikz_code


# constants
DARKER_GRAY = (25,25,25)
DARK_GRAY = (50,50,50)
GRAY = (120,120,120)
LIGHT_GRAY = (175,175,175)
WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (100,100,200)
DARK_BLUE = (50,50,100)
RED = (200,100,100)


# initialisation of Pygame
pg.init()
clock = pg.time.Clock()

# Define a font (monospace like code)
font = pg.font.Font(pg.font.match_font("courier"), 16)  # Use "Courier New" or a similar font

# screen options
screen = pg.display.set_mode((1080, 720), RESIZABLE, 32)

# toolbar
TOOLBAR_WIDTH_RATIO = 0.2  # 20% of the screen width
TOOLBAR_WIDTH = TOOLBAR_WIDTH_RATIO * screen.get_width()  # pixels
toolbar = pg.Surface((TOOLBAR_WIDTH, screen.get_height()))
toolbar.fill(GRAY)

# display is the surface where the circuit is drawn
height_ratio = 0.6
display = pg.Surface((screen.get_width() - TOOLBAR_WIDTH, int(screen.get_height()*height_ratio)))
display_rect = pg.Rect((TOOLBAR_WIDTH, 0), display.get_size())

# grid inside display
CELL_SIZE = 80
GRID_SIZE = (display.get_width() // CELL_SIZE, display.get_height() // CELL_SIZE)  # number of cells

# console is the surface where the tikz code is written
console = pg.Surface((screen.get_width() - TOOLBAR_WIDTH, int(screen.get_height()*(1-0.6))))
pg.display.set_caption("Circuit Latex Editor")
console.fill(LIGHT_GRAY)


# componants
componant_selected = None  # str (ex: "wire" or "inductor")
# wires
creating_componant = False
WIRE_WIDTH = 5
wires = []  # list of tuple(start pos[np array], end pos[np array])
# resistors
resistors = []  # list of tuple(start pos[np array], end pos[np array])
RESISTOR_WIDTH_RATIO = 0.75
RESISTOR_WIDTH = RESISTOR_WIDTH_RATIO * CELL_SIZE
RESISTOR_HEIGHT_RATIO = 2/5
RESISTOR_HEIGHT = RESISTOR_WIDTH * RESISTOR_HEIGHT_RATIO

# boutons
buttons = []  # list of objects from class Buttons
for i, name in enumerate(["wire", "resistor", "capacitor", "inductor", "generator"]):
    buttons.append(Buttons(name, i+1))



# main loop
running = True
while running:
    for event in pg.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        if event.type == WINDOWRESIZED:  # update surfaces
            TOOLBAR_WIDTH = TOOLBAR_WIDTH_RATIO * screen.get_width() 
            toolbar = pg.Surface((TOOLBAR_WIDTH, screen.get_height()))
            display = pg.Surface((screen.get_width() - TOOLBAR_WIDTH, int(screen.get_height()*height_ratio)))
            display_rect = pg.Rect((TOOLBAR_WIDTH, 0), display.get_size())
            console = pg.Surface((screen.get_width() - TOOLBAR_WIDTH, int(screen.get_height()*(1-0.6))))
            GRID_SIZE = (display.get_width() // CELL_SIZE, display.get_height() // CELL_SIZE)  # number of cells
        if event.type == MOUSEMOTION:
             mouse_pos = np.array(pg.mouse.get_pos())
        if event.type == MOUSEBUTTONDOWN:
            # detect buttons click
            for button in buttons:
                if button.rect.collidepoint(mouse_pos):
                    componant_selected = button.button_clicked()
                    print(componant_selected)

    # componant selected --> ready to create if the user clicks
    if componant_selected:
        # left click --> create a componant
        if pg.mouse.get_just_pressed()[0] and display_rect.collidepoint(mouse_pos):
            start_pos = snap_to_grid(mouse_pos)
            if componant_selected == "wire":
                wires.append(np.array([start_pos, mouse_pos]))
            elif componant_selected == "resistor":
                resistors.append([start_pos, mouse_pos])
            creating_componant = True
        elif creating_componant:  # update the componant pos that is currently created
            if componant_selected == "wire":
                wires[-1][1] = snap_to_grid(mouse_pos)
            elif componant_selected == "resistor":
                resistors[-1][1] = snap_to_grid(mouse_pos)

        # release left click --> remove componant if not valid
        if pg.mouse.get_just_released()[0]:
            # check if componant inside display and is long enough
            if creating_componant and (not display_rect.collidepoint(mouse_pos) or np.linalg.norm((start_pos-mouse_pos)) < CELL_SIZE/2):
                print("not long enough or outside display")
                if componant_selected == "wire":
                    wires.pop(-1)  # remove the componant that was being created
                elif componant_selected == "resistor":
                    wires.pop(-1)  # remove the componant that was being created
            else:
                code = generate_tikz_code()
                console.fill(LIGHT_GRAY)
                console.blit(code, code.get_rect())
            creating_componant = False


    # backgtound colors
    display.fill(DARKER_GRAY)

    draw_grid()
    
    draw_wires()

    draw_resistors()


    # blit surfaces onto the screen
    screen.blit(display, display_rect.topleft)
    screen.blit(console, (TOOLBAR_WIDTH, display.get_height()))
    screen.blit(toolbar, (0,0))

    # screen update
    pg.display.update()
    clock.tick(25)


pg.quit()
""""
TODO :
    * select componants (remove the selected componants)
    * modify wires
    * Add options for componants (different types of generators, label options ...)
    * Add componants (diode, transistor)
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
        self.componant = Componant(type=type, color=BLACK, dest_surf=self.surf, start_pos=np.array([0.1*self.rect.width, self.rect.height/2]), end_pos=np.array([0.9*self.rect.width, self.rect.height/2]))
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
        self.componant.draw()
        # draw button onto the toolbar
        toolbar.blit(self.surf, self.rect)
        # draw borders if selected
        if self.selected:
            pg.draw.rect(toolbar, DARK_BLUE, self.rect, WIRE_WIDTH)
        

class Componant:
    def __init__(self, start_pos=[0,0], end_pos=[0,0], type="wire", label_option="", dest_surf=None, color=None):
        """
        surf option: where to blit the componant (also used to know if it should be included in tikz code)
        """
        self.dest_surf = dest_surf
        self.color = color
        self.type = type
        self.start = start_pos
        self.end = end_pos
        self.label_option = label_option  # "_ - * $" bottom/left ; middle ; top/right ; math mode ; 

        if self.type == "wire":
            self.tikz_type = "short"
        elif type=="resistor":
            self.tikz_type = "R"
        elif type=="inductor":
            self.tikz_type = "L"
        elif type=="capacitor":
            self.tikz_type = "C"
        elif type=="generator":
            self.tikz_type = "voltage source"
        else:
            self.tikz_type = ""


    def draw(self):
        if self.type == "wire":
            self.draw_wire()
        elif self.type == "resistor":
            self.draw_resistor()
        elif self.type == "inductor":
            self.draw_inductor()
        elif self.type == "capacitor":
            self.draw_capacitor()
        elif self.type == "generator":
            self.draw_generator()


    def draw_wire(self):
        """draw wire onto the display"""
        if self.dest_surf == display:
            start = self.start-np.array([TOOLBAR_WIDTH, 0])
            end = self.end-np.array([TOOLBAR_WIDTH, 0])
        else:
            start, end = self.start, self.end

        draw_line_round_corners(self.dest_surf, start, end, self.color, WIRE_WIDTH)


    def draw_resistor(self):
        """
        blit a resistor onto self.dest_surf
        """
        if self.dest_surf == display:
            pos1 = self.start-np.array([TOOLBAR_WIDTH, 0])
            pos2 = self.end-np.array([TOOLBAR_WIDTH, 0])
        else:
            pos1 = self.start
            pos2 = self.end

        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        # Use np.arctan2 to properly compute the angle
        alpha = np.arctan2(dy, dx)
        # l is the lenght of branches
        l = (np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2) - RESISTOR_WIDTH) / 2
        R_left, R_right = [pos1[0]+l*np.cos(alpha), self.start[1]+l*np.sin(alpha)], [pos1[0]+(l+RESISTOR_WIDTH)*np.cos(alpha), pos1[1]+(l+RESISTOR_WIDTH)*np.sin(alpha)]
        # branches
        draw_line_round_corners(self.dest_surf, pos1, R_left, self.color, width=WIRE_WIDTH)
        draw_line_round_corners(self.dest_surf, R_right, pos2, self.color, width=WIRE_WIDTH)
        # rectangle ABCD
        A = [R_left[0]-(RESISTOR_HEIGHT/2)*np.sin(alpha), R_left[1]+(RESISTOR_HEIGHT/2)*np.cos(alpha)]
        B = [R_left[0]+(RESISTOR_HEIGHT/2)*np.sin(alpha), R_left[1]-(RESISTOR_HEIGHT/2)*np.cos(alpha)]
        C = [R_right[0]+(RESISTOR_HEIGHT/2)*np.sin(alpha), R_right[1]-(RESISTOR_HEIGHT/2)*np.cos(alpha)]
        D = [R_right[0]-(RESISTOR_HEIGHT/2)*np.sin(alpha), R_right[1]+(RESISTOR_HEIGHT/2)*np.cos(alpha)]
        pg.draw.polygon(self.dest_surf, self.color, [A,B,C,D], width=WIRE_WIDTH)


    def draw_inductor(self):
        """
        blit an inductor onto self.dest_surf
        """
        if self.dest_surf == display:
            pos1 = self.start-np.array([TOOLBAR_WIDTH, 0])
            pos2 = self.end-np.array([TOOLBAR_WIDTH, 0])
        else:
            pos1 = self.start
            pos2 = self.end

        dx, dy = pos2[0] - pos1[0], pos2[1] - pos1[1]
        # Use np.arctan2 to properly compute the angle
        alpha = np.arctan2(dy, dx)
        # l is the lenght of branches
        l = (np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2) - RESISTOR_WIDTH) / 2
        R_left= [pos1[0]+l*np.cos(alpha), self.start[1]+l*np.sin(alpha)]
        R_right =  [pos1[0]+(l+RESISTOR_WIDTH)*np.cos(alpha), pos1[1]+(l+RESISTOR_WIDTH)*np.sin(alpha)]
        # branches
        draw_line_round_corners(self.dest_surf, pos1, R_left, self.color, width=WIRE_WIDTH)
        draw_line_round_corners(self.dest_surf, R_right, pos2, self.color, width=WIRE_WIDTH)
        # Centres des cercles pour les arcs
        arc_centers = []
        for i in range(3):
            offset = (i + 0.5) * (RESISTOR_WIDTH / 3)  # Position de chaque arc
            center = np.array([
                R_left[0] + offset * np.cos(alpha) + (RESISTOR_HEIGHT / 2) * np.sin(alpha),
                R_left[1] + offset * np.sin(alpha) - (RESISTOR_HEIGHT / 2) * np.cos(alpha)
            ])
            arc_centers.append(center)

        # Dessiner les arcs avec correction de l'alignement
        for center in arc_centers:
            rect = pg.Rect(0, 0, RESISTOR_HEIGHT, RESISTOR_HEIGHT)
            rect.center = (center[0] - (RESISTOR_HEIGHT/2)*np.sin(alpha),
                        center[1] + (RESISTOR_HEIGHT/2)*np.cos(alpha))  # Ajustement ici
            pg.draw.arc(self.dest_surf, self.color, rect, -alpha, -alpha+np.pi, WIRE_WIDTH)


    def draw_capacitor(self):
        """
        blit an capacitor onto self.dest_surf
        """
        if self.dest_surf == display:
            pos1 = self.start-np.array([TOOLBAR_WIDTH, 0])
            pos2 = self.end-np.array([TOOLBAR_WIDTH, 0])
        else:
            pos1 = self.start
            pos2 = self.end

        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        # Use np.arctan2 to properly compute the angle
        alpha = np.arctan2(dy, dx)
        # l is the lenght of branches
        l = (np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2) - CAPACITOR_WIDTH) / 2
        R_left, R_right = [pos1[0]+l*np.cos(alpha), self.start[1]+l*np.sin(alpha)], [pos1[0]+(l+CAPACITOR_WIDTH)*np.cos(alpha), pos1[1]+(l+CAPACITOR_WIDTH)*np.sin(alpha)]
        # branches
        draw_line_round_corners(self.dest_surf, pos1, R_left, self.color, width=WIRE_WIDTH)
        draw_line_round_corners(self.dest_surf, R_right, pos2, self.color, width=WIRE_WIDTH)
        # rectangle ABCD
        A = [R_left[0]-(CAPACITOR_HEIGH/2)*np.sin(alpha), R_left[1]+(CAPACITOR_HEIGH/2)*np.cos(alpha)]
        B = [R_left[0]+(CAPACITOR_HEIGH/2)*np.sin(alpha), R_left[1]-(CAPACITOR_HEIGH/2)*np.cos(alpha)]
        C = [R_right[0]+(CAPACITOR_HEIGH/2)*np.sin(alpha), R_right[1]-(CAPACITOR_HEIGH/2)*np.cos(alpha)]
        D = [R_right[0]-(CAPACITOR_HEIGH/2)*np.sin(alpha), R_right[1]+(CAPACITOR_HEIGH/2)*np.cos(alpha)]
        # draw two lines
        draw_line_round_corners(self.dest_surf, A, B, self.color, width=WIRE_WIDTH)
        draw_line_round_corners(self.dest_surf, C, D, self.color, width=WIRE_WIDTH)


    def draw_generator(self):
        """
        blit a generator onto self.dest_surf
        """
        if self.dest_surf == display:
            pos1 = self.start-np.array([TOOLBAR_WIDTH, 0])
            pos2 = self.end-np.array([TOOLBAR_WIDTH, 0])
        else:
            pos1 = self.start
            pos2 = self.end

        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        # Use np.arctan2 to properly compute the angle
        alpha = np.arctan2(dy, dx)
        # l is the lenght of branches
        l = (np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2) - RESISTOR_WIDTH) / 2
        # branches
        R_left= np.array([pos1[0]+l*np.cos(alpha), self.start[1]+l*np.sin(alpha)])
        R_right =  np.array([pos1[0]+(l+RESISTOR_WIDTH)*np.cos(alpha), pos1[1]+(l+RESISTOR_WIDTH)*np.sin(alpha)])  
        draw_line_round_corners(self.dest_surf, pos1, R_left, self.color, width=WIRE_WIDTH)
        draw_line_round_corners(self.dest_surf, R_right, pos2, self.color, width=WIRE_WIDTH)
        # circle
        radius = np.linalg.norm(R_right-R_left)/2
        pg.draw.circle(self.dest_surf, self.color, (R_right+R_left)/2, radius, WIRE_WIDTH)


def draw_grid():
    """
    draw grid onto the display
    """
    for x in range(CELL_SIZE, CELL_SIZE*(GRID_SIZE[0]+1), CELL_SIZE):  # vertical lines
        pg.draw.line(display, DARK_GRAY, (x, 0), (x, display.get_height()), 1)
    for y in range(CELL_SIZE, CELL_SIZE*(GRID_SIZE[1]+1), CELL_SIZE):  # horizontal lines
        pg.draw.line(display, DARK_GRAY, (0, y), (display.get_width(), y), 1)


def snap_to_grid(coord):
    coord[1] = CELL_SIZE * round(coord[1] / CELL_SIZE)
    coord[0] = TOOLBAR_WIDTH + CELL_SIZE * round((coord[0] - TOOLBAR_WIDTH) / CELL_SIZE)
    return coord


def draw_line_round_corners(surf, start_pos, end_pos, color, width):
    pg.draw.line(surf, color, start_pos, end_pos, width)
    pg.draw.circle(surf, color, start_pos, width//2)  # add // 2 to get a simple rounded edge 
    pg.draw.circle(surf, color, end_pos, width//2)  # add // 2 to get a simple rounded edge 


def generate_tikz_code():
    """
    Génère le code TikZ pour les fils dessinés.
    """
    TIKZ_SCALE_FACTOR = 2
    # find the coordinate of the componant at the top left (used to simplify tikz code)
    offset = np.array(screen.get_size())
    for componant in componants:
        offset[0] = min(offset[0], min(componant.start[0], componant.end[0])) 
        offset[1] = min(offset[1], min(componant.start[1], componant.end[1]))
    offset[0] = offset[0] - TOOLBAR_WIDTH
    offset = offset // CELL_SIZE  # convert to tikz coordinate

    # code
    tikz_code = "\\documentclass[tikz,border=10pt]{standalone}\n\n"
    tikz_code += "\\usepackage[european, straightvoltages, RPvoltages, cute inductor]{circuitikz}  % RPvoltages definie la convention des dipoles (sens tension faux sinon)\n\n"
    tikz_code += "\\begin{document}\n\n    \\begin{tikzpicture}\n"
    for componant in componants:
        start = ((componant.start - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset) * TIKZ_SCALE_FACTOR
        end = ((componant.end - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset) * TIKZ_SCALE_FACTOR
        label = ""if componant.type=="wire" else f", l={componant.tikz_type}"
        tikz_code += f"        \\draw ({start[0]:.1f}, {-start[1]:.1f}) to[{componant.tikz_type}{label}] ({end[0]:.1f}, {-end[1]:.1f});\n"

    tikz_code += "    \\end{tikzpicture}\n\n\\end{document}"
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
creating_componant = False
componants = []  # list of object (class: Componant)
componant_selected = None  # str (ex: "wire" or "inductor")
# wires
WIRE_WIDTH = 5
# resistors dimensions
RESISTOR_WIDTH_RATIO = 0.75
RESISTOR_WIDTH = RESISTOR_WIDTH_RATIO * CELL_SIZE
RESISTOR_HEIGHT_RATIO = 2/5
RESISTOR_HEIGHT = RESISTOR_WIDTH * RESISTOR_HEIGHT_RATIO
# capacitors dimensions
CAPACITOR_WIDTH_RATIO = 1/3
CAPACITOR_WIDTH = CAPACITOR_WIDTH_RATIO * CELL_SIZE
CAPACITOR_HEIGHT_RATIO = 4/3
CAPACITOR_HEIGH = CAPACITOR_WIDTH * CAPACITOR_HEIGHT_RATIO

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
            componants.append(Componant(start_pos=start_pos, end_pos=mouse_pos, type=componant_selected, dest_surf=display, color=BLUE))
            creating_componant = True
        elif creating_componant:  # update the componant pos that is currently created
            componants[-1].end = snap_to_grid(mouse_pos)

        # release left click --> remove componant if not valid
        if pg.mouse.get_just_released()[0]:
            # check if componant inside display and is long enough
            if creating_componant and (not display_rect.collidepoint(mouse_pos) or np.linalg.norm((start_pos-mouse_pos)) < CELL_SIZE/2):
                print("not long enough or outside display")
                componants.pop(-1)  # remove the componant that was being created
            else:
                code = generate_tikz_code()
                console.fill(LIGHT_GRAY)
                console.blit(code, code.get_rect())
            creating_componant = False


    # backgtound colors
    display.fill(DARKER_GRAY)

    draw_grid()
    
    # draw componants
    for componant in componants:
        componant.draw()


    # blit surfaces onto the screen
    screen.blit(display, display_rect.topleft)
    screen.blit(console, (TOOLBAR_WIDTH, display.get_height()))
    screen.blit(toolbar, (0,0))

    # screen update
    pg.display.update()
    clock.tick(25)


pg.quit()
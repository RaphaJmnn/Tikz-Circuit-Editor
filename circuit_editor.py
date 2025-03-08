""""
TODO :
    * select components (remove the selected components)
    * modify wires
    * Add options for components (different types of generators, label options ...)
    * Add components (diode, transistor)
"""

import pygame as pg
from pygame.locals import *
import pygame_gui
import numpy as np


class Buttons:
    def __init__(self, type="wire", position=1):
        self.position = position
        self.type = type
        self.selected = False
        self.VERTICAL_SPACING = 20
        self.WIDTH_RATIO = 0.8
        self.SIZE = np.array([TOOLBAR_WIDTH * self.WIDTH_RATIO, self.VERTICAL_SPACING*4])
        self.surf = pg.Surface(self.SIZE)
        self.rect = pg.Rect(((TOOLBAR_WIDTH-self.SIZE[0])/2, (self.VERTICAL_SPACING+self.SIZE[1])*self.position), self.SIZE) 
        self.component = Component(type=type, color=BLACK, dest_surf=self.surf, start_pos=np.array([0.1*self.rect.width, self.rect.height/2]), end_pos=np.array([0.9*self.rect.width, self.rect.height/2]))
        self.update()

    
    def button_clicked(self):
        """
        This function is called every time the user clicks.
        It updates the buttons state (selected or not) --> update visual (calls update function)
        return the type of component selected (or None if no component is selected)
        """
        
        self.selected = not self.selected  # select/deselect component clicked

        # deselect every component when another is clicked
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


    def update_size(self):
        self.SIZE = np.array([TOOLBAR_WIDTH * self.WIDTH_RATIO, self.VERTICAL_SPACING*4])
        self.surf = pg.Surface(self.SIZE)
        self.rect = pg.Rect(((TOOLBAR_WIDTH-self.SIZE[0])/2, (self.VERTICAL_SPACING+self.SIZE[1])*self.position), self.SIZE) 
        self.component.start_pos = np.array([0.1*self.rect.width, self.rect.height/2])
        self.component.end_pos = np.array([0.9*self.rect.width, self.rect.height/2])
        self.component.dest_surf = self.surf


    def update(self):
        # draw button background
        self.surf.fill(RED)
        # draw button symbol (TODO)
        self.component.draw()
        # draw button onto the toolbar
        toolbar.blit(self.surf, self.rect)
        # draw borders if selected
        if self.selected:
            pg.draw.rect(toolbar, DARK_BLUE, self.rect, WIRE_WIDTH)
        

class Component:
    def __init__(self, start_pos=[0,0], end_pos=[0,0], type="wire", label_option="", dest_surf=None, color=None):
        """
        surf option: where to blit the component (also used to know if it should be included in tikz code)
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


def display_tikz_code():
    """
    Génère et Affiche le code Tikz.
    """
    global text_box, tikz_code

    TIKZ_SCALE_FACTOR = 2
    # find the coordinate of the component at the top left (used to simplify tikz code)
    offset = np.array(screen.get_size())
    for component in components:
        offset[0] = min(offset[0], min(component.start[0], component.end[0])) 
        offset[1] = min(offset[1], min(component.start[1], component.end[1]))
    offset[0] = offset[0] - TOOLBAR_WIDTH
    offset = offset // CELL_SIZE  # convert to tikz coordinate

    # code
    tikz_code = "\\documentclass[tikz,border=10pt]{standalone}\n\n"
    tikz_code += "\\usepackage[european, straightvoltages, RPvoltages, cute inductor]{circuitikz}\n\n"
    tikz_code += "\\begin{document}\n\n    \\begin{tikzpicture}\n"
    print(len(components))
    for component in components:
        start = ((component.start - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset) * TIKZ_SCALE_FACTOR
        end = ((component.end - np.array([TOOLBAR_WIDTH, 0])) // CELL_SIZE - offset) * TIKZ_SCALE_FACTOR
        label = ""if component.type=="wire" else f", l={component.tikz_type}"
        tikz_code += f"        \\draw ({start[0]:.1f}, {-start[1]:.1f}) to[{component.tikz_type}{label}] ({end[0]:.1f}, {-end[1]:.1f});\n"
    tikz_code += "    \\end{tikzpicture}\n\n\\end{document}"

    text_box.set_text(tikz_code)


def valid_placement():
    """
    Test if the component placed (when mouse released) is not too short
    not outside display and not overlapping with another component.
    return True or False
    """    
    for component in components[:-1]:  # iterate trought all elements exept the last one
        if (np.array_equal(components[-1].start, component.start) and np.array_equal(components[-1].end, component.end)) or \
            (np.array_equal(components[-1].start, component.end) and np.array_equal(components[-1].end, component.start)):
            return False
        
    if not display_rect.collidepoint(mouse_pos) or np.linalg.norm((start_pos-mouse_pos)) < CELL_SIZE/2:
        return False
    
    return True


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
FPS = 25
screen = pg.display.set_mode((1080, 720), RESIZABLE, 32)
pg.display.set_caption("Circuit Latex Editor")

# toolbar
TOOLBAR_WIDTH_RATIO = 0.2  # 20% of the screen width
TOOLBAR_WIDTH = TOOLBAR_WIDTH_RATIO * screen.get_width()  # pixels
toolbar = pg.Surface((TOOLBAR_WIDTH, screen.get_height()))
toolbar.fill(GRAY)

# display is the surface where the circuit is drawn
height_ratio = 0.6
display = pg.Surface((screen.get_width() - TOOLBAR_WIDTH, int(screen.get_height()*height_ratio)))
display_rect = pg.Rect((TOOLBAR_WIDTH, 0), display.get_size())

# Create a UIManager
UI_manager = pygame_gui.UIManager((1080, 720))
tikz_code = ""
text_box = pygame_gui.elements.UITextBox(tikz_code, pg.Rect(TOOLBAR_WIDTH, display.height, display.width, screen.height-display.height), UI_manager)

# grid inside display
CELL_SIZE = 80
GRID_SIZE = (display.get_width() // CELL_SIZE, display.get_height() // CELL_SIZE)  # number of cells

# components
creating_component = False
components = []  # list of object (class: component)
component_selected = None  # str (ex: "wire" or "inductor")
SELECT_RADIUS = 10  # px
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
    buttons.append(Buttons(name, i+1))  # i is for the position of the buttons


# main loop
running = True
while running:
    # FPS
    time_delta = clock.tick(FPS) / 1000.0

    for event in pg.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        if event.type == WINDOWRESIZED:  # update surfaces
            # toolbar
            TOOLBAR_WIDTH = TOOLBAR_WIDTH_RATIO * screen.get_width() 
            toolbar = pg.Surface((TOOLBAR_WIDTH, screen.get_height()))
            toolbar.fill(GRAY)
            for button in buttons:
                button.update_size()
                button.update()
            # display
            display = pg.Surface((screen.get_width() - TOOLBAR_WIDTH, int(screen.get_height()*height_ratio)))
            display_rect = pg.Rect((TOOLBAR_WIDTH, 0), display.get_size())
            GRID_SIZE = (display.get_width() // CELL_SIZE, display.get_height() // CELL_SIZE)  # number of cells
            # Redraw the components on the new display surface (size changed)
            for component in components:
                component.dest_surf = display
                component.start = snap_to_grid(component.start)
                component.end = snap_to_grid(component.end)

            # text box
            UI_manager.set_window_resolution((screen.width, screen.height))
            text_box.set_relative_position((TOOLBAR_WIDTH, display.height)) 
            text_box.set_dimensions((display.width, screen.height-display.height))


        if event.type == MOUSEMOTION:  # get mouse pos each frame
             mouse_pos = np.array(pg.mouse.get_pos())
        if event.type == MOUSEBUTTONDOWN:
            # detect buttons click
            for button in buttons:
                if button.rect.collidepoint(mouse_pos):
                    component_selected = button.button_clicked()

        # Pass events to pygame_gui
        UI_manager.process_events(event)    

    # Update the UIUI_UI_manager
    UI_manager.update(time_delta)


    # component selected --> ready to create if the user clicks
    if component_selected:
        # left click --> create a component
        if pg.mouse.get_just_pressed()[0] and display_rect.collidepoint(mouse_pos):
            start_pos = snap_to_grid(mouse_pos)
            components.append(Component(start_pos=start_pos, end_pos=mouse_pos, type=component_selected, dest_surf=display, color=BLUE))
            creating_component = True
        elif creating_component and display_rect.collidepoint(mouse_pos):  # update the component pos that is currently created
            components[-1].end = snap_to_grid(mouse_pos)

        # release left click --> remove component if not valid
        if pg.mouse.get_just_released()[0]:
            # check if component inside display and is long enough and not at the same place as another
            if creating_component and not valid_placement():
                components.pop(-1)  # remove the component that was being created
            elif display_rect.collidepoint(mouse_pos):
                display_tikz_code()           
            creating_component = False

    # edit mode (no componant selected and mouse on display)
    elif display_rect.collidepoint(mouse_pos):
        # check if the mouse is over the start pos or end pos of a component to modify it
        for compopent in components:
            dist1 = np.linalg.norm(mouse_pos-component.start)  # distance between mouse and start handle
            dist2 = np.linalg.norm(mouse_pos-component.end)  # distance between mouse and end handle
            if dist1 <= SELECT_RADIUS:
                pass
            elif dist2 <= SELECT_RADIUS:
                pass


    # backgtound colors
    display.fill(DARKER_GRAY)

    draw_grid()

    # draw components
    for component in components:
        component.draw()
    
    UI_manager.draw_ui(screen)

    # blit surfaces onto the screen
    screen.blit(display, display_rect.topleft)
    #screen.blit(console, (TOOLBAR_WIDTH, display.get_height()))
    screen.blit(toolbar, (0,0))

    # screen update
    pg.display.flip()


pg.quit()
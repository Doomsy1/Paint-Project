from random import randint
from pygame import *
from config import *
from selection import selection_tool
from math import ceil, hypot
from collections import deque
from utils import draw_rounded_line, fit_img_to_rect, write_centered_text

# tools dictionary
# description: what does the tool do \n how to use it
tools = {
    "pencil": {
        "rect": Rect(10,105,40,40),
        "description": "Draws lines\nClick and drag to draw"
    },
    "eraser": {
        "rect": Rect(60,105,40,40),
        "description": "Erases lines\nClick and drag to erase"
    },
    "spray":{
        "rect": Rect(10,155,40,40),
        "description": "Sprays paint\nClick and drag to spray"
    },
    "paint_brush":{
        "rect": Rect(60,155,40,40),
        "description": "Paints lines\nClick and drag to paint"
    },
    "line":{
        "rect": Rect(10,205,40,40),
        "description": "Draws lines\nClick and drag to draw\nHold shift to snap to 90 degrees"
    },
    "rect":{
        "rect": Rect(60,205,40,40),
        "description": "Draws rectangles\nClick and drag to draw\nHold shift to draw squares"
    },
    "ellipse":{
        "rect": Rect(10,255,40,40),
        "description": "Draws ellipses\nClick and drag to draw\nHold shift to draw circles"
    },
    "eye_dropper":{
        "rect": Rect(60,255,40,40),
        "description": "Selects a colour\nClick to select a colour"
    },
    "fireworks":{
        "rect": Rect(10,305,40,40),
        "description": "Draws fireworks\nClick to draw"
    },
    "air_brush":{
        "rect": Rect(60,305,40,40),
        "description": "Draws air brush\nClick to draw"
    },
    "paint_bucket":{
        "rect": Rect(10,355,40,40),
        "description": "Fills an area with colour\nClick to fill"
    },
    "fill_screen":{
        "rect": Rect(60,355,40,40),
        "description": "Fills the screen with colour\nClick to fill"
    },
    "stamp": {
        "rect": Rect(585,560,205,125),
        "description": "Stamps an image\nDrag and drop to stamp"
    },
    "select": {
        "rect": Rect(10,405,90,40),
        "description": "Selects an area\nClick and drag to select\nGrab resize handles to resize"
    }
}

# rect for the description of the tools
description_rect = Rect(10, 560, 400, 65)

# Load images once and store them (except for the stamp tool)
tool_images = {}
for tool in tools:
    if tool != "stamp":
        tool_images[tool] = transform.scale(image.load(f"assets/tools/{tool}.png"), (40, 40))

def tool_change(tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    mouse_up = button_data["mouse_up"]
    og_tool = tool_settings["tool"]

    if mouse_up: # check if the user has clicked on a tool
        for tool in tools:   
            if tools[tool]["rect"].collidepoint(mx, my):
                global select_state
                global move_start
                global og_start
                global clipboard
                select_state = 0
                move_start = (0, 0)
                og_start = (0, 0)
                clipboard = None
                return tool
    return og_tool

def draw_stamp_preview(screen, tool_settings):
    current_stamp_img = tool_settings["stamp"]
    # draw the current stamp in the stamp tool rect
    stamp_rect = tools["stamp"]["rect"]

    # make a background for the stamp preview
    draw.rect(screen, BG_COLOUR, stamp_rect)

    # center the stamp in the rect and scale it to fit while maintaining aspect ratio
    fit_img_to_rect(screen, current_stamp_img, stamp_rect)

def draw_tools(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    # Use the pre-loaded images
    description = "Hover over a tool to see its description"
    for tool in tools: # draw the backgrounds of the tools then the images then the outlines and descriptions
        rect = tools[tool]["rect"]

        # draw the background of the tool
        draw.rect(screen, BG_COLOUR, rect)
        
        # draw the image of the tool
        if tool != "stamp": # draw the pre-loaded images
            img_rect = tools[tool]["rect"].inflate(-10, -10)
            fit_img_to_rect(screen, tool_images[tool], img_rect)
        elif tool == "stamp": # stamp needs to be drawn differently as it is not pre-loaded
            draw_stamp_preview(screen, tool_settings)

        # draw the outline of the tool
        if rect.collidepoint(mx, my):
            draw.rect(screen, HOVER_COLOUR, rect, 2)
            description = tools[tool]["description"]
        else:
            draw.rect(screen, UNSELECED_COLOUR, rect, 2)

    write_description(screen, text = description)
    draw_selected_tool(screen, tool_settings)

def draw_selected_tool(screen, tool_settings):
    tool = tool_settings["tool"]
    
    # draw an outline around the selected tool
    draw.rect(screen, SELECTED_COLOUR, tools[tool]["rect"], 2)
    
def write_description(screen, text=None):
        
    # draw the description of the tool
    text_rect = description_rect.inflate(-5, -5)

    # draw a background for the description
    draw.rect(screen, BG_COLOUR, description_rect)
    if text: # if there is a description to write
        write_centered_text(screen, text, text_rect, (0, 0, 0))
    else: # if there is no description to write
        write_centered_text(screen, tools[tool]["description"], text_rect, (0, 0, 0))

    # draw an outline around the description rect
    draw.rect(screen, (0, 0, 0), description_rect, 2)


def tool_manager(screen, canvas_rect, button_data, tool_settings):
    mouse_up = button_data["mouse_up"]
    mb = button_data["mb"]
    tool = tool_settings["tool"]
    col = tool_settings["col"]
    update = False

    if mb[0] or mouse_up or tool == "select": # check if the user is using a tool
        match tool: # check which tool is being used
            case "pencil":
                pencil_tool(screen, tool_settings, button_data)
            case "eraser":
                erase_tool(screen, tool_settings, button_data)
            case "spray":
                spray_tool(screen, tool_settings, button_data)
            case "paint_brush":
                paint_brush_tool(screen, tool_settings, button_data)
            case "line":
                line_tool(screen, tool_settings, button_data)
            case "rect":
                rect_tool(screen, tool_settings, button_data)
            case "ellipse":
                elipse_tool(screen, tool_settings, button_data)
            case "eye_dropper":
                col = eye_dropper_tool(screen, button_data)
            case "fireworks":
                fireworks_tool(screen, tool_settings, button_data)
            case "air_brush":
                air_brush_tool(screen, tool_settings, button_data)
            case "paint_bucket":
                paint_bucket_tool(screen, canvas_rect, tool_settings, button_data)
            case "fill_screen":
                fill_screen_tool(screen, canvas_rect, tool_settings, button_data)
            case "stamp":
                stamp_tool(screen, canvas_rect, tool_settings, button_data)
            case "select":
                update = selection_tool(screen, canvas_rect, button_data)
    return col, update # return the colour and whether the canvas needs to be updated

def pencil_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    omx, omy = button_data["omx"], button_data["omy"]
    col = tool_settings["col"]

    # draw a line from the previous mouse position to the current mouse position
    draw.line(screen, col, (omx, omy), (mx, my))

def erase_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    radius = tool_settings["radius"]

    # draw a white circle at the mouse position
    draw.circle(screen, (255, 255, 255), (mx, my), radius)

    # draw a white line from the previous mouse position to the current mouse position
    draw_rounded_line(screen, (255,255,255), (button_data["omx"], button_data["omy"]), (mx, my), radius)

def spray_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    radius = tool_settings["radius"]
    col = tool_settings["col"]

    # time to fill the circle (frames) used to keep the circle from being filled too quickly or too slowly
    time_to_fill = 240

    # number of loops pper frame to fill the circle in the time_to_fill
    number_of_loops = 4 * radius**2 // time_to_fill
    for _ in range(number_of_loops):
        x=randint(-radius,radius)
        y=randint(-radius,radius)
        if hypot(x,y)<=radius:
            # draw a circle with radius of 1 to 3 at the random point
            circle_radius = randint(1, 3)
            draw.circle(screen,col,(mx+x,my+y), circle_radius)
        
def paint_brush_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    radius = tool_settings["radius"]
    col = tool_settings["col"]

    # draw a circle at the mouse position
    draw.circle(screen, col, (mx, my), radius)

    # draw a line from the previous mouse position to the current mouse position
    draw_rounded_line(screen, col, (button_data["omx"], button_data["omy"]), (mx, my), radius)

def line_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    dmx, dmy = button_data["dmx"], button_data["dmy"]
    shift = button_data["shift"]
    radius = tool_settings["radius"]
    col = tool_settings["col"]

    if shift:
        # snap to 90 degree angles
        if abs(mx - dmx) > abs(my - dmy):
            my = dmy
        else:
            mx = dmx

    # draw a line from the mouse position to the previous mouse position
    draw_rounded_line(screen, col, (dmx, dmy), (mx, my), radius)


def rect_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    dmx, dmy = button_data["dmx"], button_data["dmy"]
    shift = button_data["shift"]
    radius = tool_settings["radius"]
    col = tool_settings["col"]
    fill = tool_settings["fill"]

    # get the top left corner of the rectangle
    left = min(mx, dmx)
    top = min(my, dmy)

    # get the width and height of the rectangle
    width = abs(mx - dmx)
    height = abs(my - dmy)

    # snap to a square if shift is held
    if shift:
        width = height = min(width, height)
        # fix the left and top values
        if mx < dmx:
            left = dmx - width
        if my < dmy:
            top = dmy - height

    # draw the rectangle
    if fill: # fill the rectangle
        draw.rect(screen, col, (left, top, width, height), 0)
    else: # draw the outline of the rectangle
        draw.rect(screen, col, (left, top, width, height), radius)

def elipse_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    dmx, dmy = button_data["dmx"], button_data["dmy"]
    shift = button_data["shift"]
    radius = tool_settings["radius"]
    col = tool_settings["col"]
    fill = tool_settings["fill"]

    # get the top left corner of the ellipse
    left = min(mx, dmx)
    top = min(my, dmy)

    # get the width and height of the ellipse
    width = abs(mx - dmx)
    height = abs(my - dmy)

    # snap to a circle if shift is held
    if shift:
        width = height = min(width, height)
        # fix the left and top values
        if mx < dmx:
            left = dmx - width
        if my < dmy:
            top = dmy - height

    # draw the ellipse
    if fill: # fill the ellipse
        draw.ellipse(screen, col, (left, top, width, height), 0)
    else: # draw the outline of the ellipse
        draw.ellipse(screen, col, (left, top, width, height), radius)

def eye_dropper_tool(screen, button_data):
    mx, my = button_data["mx"], button_data["my"]

    # get the colour of the pixel at the mouse position
    col = screen.get_at((mx, my))[:3]
    return col

def fireworks_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    radius = tool_settings["radius"]
    col = tool_settings["col"]

    # number of loops to draw the fireworks
    loops = ceil(radius/25)
    for _ in range(loops):
        # change the colour of the fireworks slightly from the original colour (+/-) and make sure it is between 0 and 255
        change = 128
        r = min(255, max(0, col[0] + randint(-change, change)))
        g = min(255, max(0, col[1] + randint(-change, change)))
        b = min(255, max(0, col[2] + randint(-change, change)))

        # pick 2 random points within the radius and draw a line with (r, g, b) between them
        # they must be within the radius of the fireworks
        x1, y1 = randint(-radius, radius), randint(-radius, radius)
        x2, y2 = randint(-radius, radius), randint(-radius, radius)
        if hypot(x1, y1) <= radius and hypot(x2, y2) <= radius:
            # draw a line with a width of 1
            draw.line(screen, (r, g, b), (mx + x1, my + y1), (mx + x2, my + y2), 1)


def air_brush_tool(screen, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    radius = tool_settings["radius"]
    col = tool_settings["col"]

    # time to fill the circle (frames) used to keep the circle from being filled too quickly or too slowly
    time_to_fill = 240

    # number of loops pper frame to fill the circle in the time_to_fill
    number_of_loops = 4 * radius**2 // time_to_fill
    for _ in range(number_of_loops):
        x=randint(-radius,radius)
        y=randint(-radius,radius)

        # make sure the random point is within the radius of the air brush
        if hypot(x,y)<=radius:
            # change the colour of the air brush slightly from the original colour (+/-) and make sure it is between 0 and 255
            change = 128
            r = min(255, max(0, col[0] + randint(-change, change)))
            g = min(255, max(0, col[1] + randint(-change, change)))
            b = min(255, max(0, col[2] + randint(-change, change)))

            # draw a circle with radius of 1 to 3 at the random point
            circle_radius = randint(1, 3)
            draw.circle(screen, (r, g, b), (mx+x,my+y), circle_radius)


def paint_bucket_tool(screen, canvas_rect, tool_settings, button_data):
    mx, my = button_data["mx"], button_data["my"]
    mouse_down = button_data["mouse_down"]
    col = tool_settings["col"]
    fill_col = screen.get_at((mx, my))[:3]

    # make sure the fill point is within the canvas
    if canvas_rect.collidepoint(mx, my) and mouse_down:
        # use a deque to store the pixels to fill
        pixels = deque([(mx, my)])
        # use a set to store the visited pixels
        # this is used to avoid adding the same pixel multiple times
        visited = set()
        while pixels:
            x, y = pixels.popleft()
            current_col = screen.get_at((x, y))[:3]
            if current_col == fill_col:
                screen.set_at((x, y), col)
                
                neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                for nx, ny in neighbors:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        pixels.append((nx, ny))

def stamp_tool(screen, canvas_rect, tool_settings, button_data):
    current_stamp_img = tool_settings["stamp"]
    stamp_size = tool_settings["stamp_size"]
    # draw the current stamp centered on the mouse
    mx, my = button_data["mx"], button_data["my"]

    # scale the stamp to fit within the canvas while maintaining aspect ratio
    scale = min(canvas_rect.width / current_stamp_img.get_width(), canvas_rect.height / current_stamp_img.get_height())

    # multiply the scale by the stamp size percentage
    scale *= stamp_size / 100

    # scale the stamp
    scaled_stamp = transform.scale(current_stamp_img, (int(current_stamp_img.get_width() * scale), int(current_stamp_img.get_height() * scale)))

    # draw the scaled stamp centered on the mouse
    screen.blit(scaled_stamp, (mx - scaled_stamp.get_width() // 2, my - scaled_stamp.get_height() // 2))

def fill_screen_tool(screen, canvas_rect, tool_settings, button_data):
    # fill the screen with the current colour
    if button_data["mouse_down"]:
        col = tool_settings["col"]
        screen.fill(col, canvas_rect)
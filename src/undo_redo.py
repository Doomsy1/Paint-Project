from pygame import *
from config import *
from utils import fit_img_to_rect

undo_rect = Rect(10, 10, 40, 40)
redo_rect = Rect(60, 10, 40, 40)

def undo_manager(screen, canvas_rect, undo_list, redo_list, button_data):
    mx, my = button_data["mx"], button_data["my"]
    mouse_up = button_data["mouse_up"]
    ctrl = button_data["ctrl"]
    shift = button_data["shift"]
    key_z = button_data["key_z"]
    key_y = button_data["key_y"]

    draw_undo_redo(screen, button_data)

    # check if the user wants to undo
    undo = ctrl and key_z or undo_rect.collidepoint(mx, my) and mouse_up
    if undo and len(undo_list) > 1: # make sure there is something to undo
        # add the current canvas to the redo list and remove it from the undo list
        redo_list.append(undo_list.pop())
        screen.blit(undo_list[-1], canvas_rect)
    
    redo = ctrl and shift and key_z or ctrl and key_y or redo_rect.collidepoint(mx, my) and mouse_up
    if redo and len(redo_list) > 0: # make sure there is something to redo
        # add the current canvas to the undo list and remove it from the redo list
        undo_list.append(redo_list.pop())
        screen.blit(undo_list[-1], canvas_rect)

    return undo_list, redo_list

# load the undo and redo images
undo_img = image.load(f"assets/buttons/undo.png")
redo_img = image.load(f"assets/buttons/redo.png")

def draw_undo_redo(screen, button_data):
    mx, my = button_data["mx"], button_data["my"]
    
    # make a background for the undo and redo buttons
    draw.rect(screen, BG_COLOUR, undo_rect)
    draw.rect(screen, BG_COLOUR, redo_rect)

    # scale the undo and redo images to fit the buttons while maintaining aspect ratio
    fit_img_to_rect(screen, undo_img, undo_rect.inflate(-5, -5))
    fit_img_to_rect(screen, redo_img, redo_rect.inflate(-5, -5))

    # draw the border around the undo and redo buttons
    draw.rect(screen, UNSELECED_COLOUR, undo_rect, 2)
    draw.rect(screen, UNSELECED_COLOUR, redo_rect, 2)

    # draw a border around the undo and redo buttons if the mouse is hovering over them
    if undo_rect.collidepoint(mx, my):
        draw.rect(screen, HOVER_COLOUR, undo_rect, 2)
    if redo_rect.collidepoint(mx, my):
        draw.rect(screen, HOVER_COLOUR, redo_rect, 2)
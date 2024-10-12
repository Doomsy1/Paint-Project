# src/selection.py 

# Selection tool
from pygame import *
from src.utils import draw_dotted_rect

selected_colour = (0, 255, 0)
unselected_colour = (255, 0, 0)

# resize handle size (RHS x RHS)
RHS = 15
RHS2 = RHS // 2

select_state = 0
# 0 = no selection
# 1 = selecting
# 2 = finished selecting (1 frame)
# 3 = selected (frames after selection is finished)
# 4 = moving selection
# 5 = finished moving selection (de-selecting) (1 frame)
# 6 = resizing selection
# 7 = finished resizing selection (1 frame)

og_start = (0, 0)
# the top left corner of the original selection rectangle before moving (used to make the old spot empty)

og_rect = None
# the original selection rectangle before moving (used to make the old spot empty)

move_start = (0, 0)
# the top left corner of the selection rectangle before moving (used to calculate the offset)

resize_start = (0, 0)
# the opposite corner of the corner being resized (used to calculate the new width and height)

resize_corner = 0
# the corner being resized
# 0 = top left
# 1 = top right
# 2 = bottom left
# 3 = bottom right

clipboard = None

def selection_tool(screen, canvas_rect, button_data):
    mx, my = button_data["mx"], button_data["my"]
    dmx, dmy = button_data["dmx"], button_data["dmy"]
    ctrl = button_data["ctrl"]
    key_z = button_data["key_z"]

    global select_state
    if ctrl and key_z:
        select_state = 0
        return False

    global move_start
    global og_start
    global og_rect
    global clipboard
    global resize_start
    global resize_corner
    select_state = selection_state_manager(button_data)

    match select_state:
        case 0: # no selection, do nothing
            pass
        case 1: # selecting
            # draw the selection rectangle preview
            top = min(my, dmy)
            left =  min(mx, dmx)
            width = abs(mx - dmx)
            height = abs(my - dmy)
            draw_dotted_rect(screen, unselected_colour, (left, top, width, height), 3)
        case 2: # finished selecting
            # if the selected area is too small, don't create a selection
            if abs(mx - dmx) < RHS or abs(my - dmy) < RHS:
                select_state = 0
                return False

            # selection rectangle
            top = min(my, dmy)
            left =  min(mx, dmx)
            width = abs(mx - dmx)
            height = abs(my - dmy)

            # make sure the selection rectangle is within the canvas
            if top < canvas_rect.y: # top
                height = top - canvas_rect.y + height
                top = canvas_rect.y
            if left < canvas_rect.x: # left
                width = left - canvas_rect.x + width
                left = canvas_rect.x
            if top + height > canvas_rect.y + canvas_rect.height: # bottom
                height = canvas_rect.y + canvas_rect.height - top
            if left + width > canvas_rect.x + canvas_rect.width: # right
                width = canvas_rect.x + canvas_rect.width - left
            
            # create the clipboard image
            clipboard = screen.subsurface(Rect(left, top, width, height)).copy()
            og_rect = clipboard.get_rect()

            # draw the selection rectangle
            draw_dotted_rect(screen, unselected_colour, (left, top, width, height), 3)
            move_start = (left, top)
            og_start = (left, top)
        case 3: # selected
            # draw the selection rectangle (use the clipboard image data to draw the selection rectangle preview)
            top = move_start[1]
            left = move_start[0]
            width = clipboard.get_width()
            height = clipboard.get_height()

            # draw a rectangle to clear the previous location
            draw.rect(screen, (255, 255, 255), (og_start[0], og_start[1], og_rect.width, og_rect.height))

            # draw the clipboard image at the current location
            screen.blit(clipboard, (left, top))
            draw_dotted_rect(screen, selected_colour, (left, top, width, height), 3)

            # draw resize boxes on the corners
            draw_resize_boxes(screen, (left, top, width, height), selected_colour)
        case 4: # moving selection
            # calculate the offset
            dx = dmx - move_start[0]
            dy = dmy - move_start[1]

            # draw the selection rectangle preview at the new location
            top = my - dy
            left = mx - dx
            width = clipboard.get_width()
            height = clipboard.get_height()

            # draw a rectangle to clear the previous location
            draw.rect(screen, (255, 255, 255), (og_start[0], og_start[1], og_rect.width, og_rect.height))

            # draw the clipboard image at the new location
            screen.blit(clipboard, (left, top))
            draw_dotted_rect(screen, selected_colour, (left, top, width, height), 3)
        case 5: # finished moving selection
            # paste the clipboard image at the new location
            dx = dmx - move_start[0]
            dy = dmy - move_start[1]
            top = my - dy
            left = mx - dx

            # draw a rectangle to clear the previous location
            draw.rect(screen, (255, 255, 255), (og_start[0], og_start[1], og_rect.width, og_rect.height))

            screen.blit(clipboard, (left, top))
            return True # return True to update the canvas
        case 6: # resizing selection
            # calculate the new width and height using move_start and resize_start
            left, top, width, height = get_resize_rect(resize_corner, resize_start, mx, my, dmx, dmy, clipboard)

            # draw a rectangle to clear the previous location
            draw.rect(screen, (255, 255, 255), (og_start[0], og_start[1], og_rect.width, og_rect.height))

            # draw the clipboard image at the new location
            scaled_clipboard = transform.scale(clipboard, (width, height))
            screen.blit(scaled_clipboard, (left, top))
            draw_dotted_rect(screen, selected_colour, (left, top, width, height), 3)

            # draw the resize boxes on the corners
            draw_resize_boxes(screen, (left, top, width, height), selected_colour)
        case 7: # finished resizing selection
            # calculate the new width and height using move_start and resize_start
            left, top, width, height = get_resize_rect(resize_corner, resize_start, mx, my, dmx, dmy, clipboard)

            # draw a rectangle to clear the previous location
            draw.rect(screen, (255, 255, 255), (og_start[0], og_start[1], og_rect.width, og_rect.height))

            # draw the clipboard image at the new location
            scaled_clipboard = transform.scale(clipboard, (width, height))
            screen.blit(scaled_clipboard, (left, top))
            draw_dotted_rect(screen, selected_colour, (left, top, width, height), 3)

            # draw the resize boxes on the corners
            draw_resize_boxes(screen, (left, top, width, height), selected_colour)

            # update the clipboard image data
            clipboard = scaled_clipboard

            # update the move_start
            move_start = (left, top)
    return False # return False to not update the canvas

def selection_state_manager(button_data):
    mx, my = button_data["mx"], button_data["my"]
    dmx, dmy = button_data["dmx"], button_data["dmy"]
    mb = button_data["mb"]
    mouse_up = button_data["mouse_up"]
    global select_state
    global move_start
    global clipboard
    global resize_start
    global resize_corner

    match select_state:
        case 0: # no selection
            if mb[0]:
                select_state = 1
        case 1: # selecting
            if mouse_up or not mb[0]:
                select_state = 2
        case 2: # finished selecting
            select_state = 3
        case 3: # selected
            if mb[0]:
                dx = dmx - move_start[0]
                dy = dmy - move_start[1]
                top = my - dy
                left = mx - dx

                # check which corner is being resized and set the resize corner
                top_left_rect = Rect(left - RHS2, top - RHS2, RHS, RHS)
                top_right_rect = Rect(left + clipboard.get_width() - RHS2, top - RHS2, RHS, RHS)
                bottom_left_rect = Rect(left - RHS2, top + clipboard.get_height() - RHS2, RHS, RHS)
                bottom_right_rect = Rect(left + clipboard.get_width() - RHS2, top + clipboard.get_height() - RHS2, RHS, RHS)
                if top_left_rect.collidepoint(mx, my): # top left being resized
                    resize_corner = 0
                    resize_start = (left + clipboard.get_width(), top + clipboard.get_height())
                    select_state = 6
                elif top_right_rect.collidepoint(mx, my): # top right being resized
                    resize_corner = 1
                    resize_start = (left, top + clipboard.get_height())
                    select_state = 6
                elif bottom_left_rect.collidepoint(mx, my): # bottom left being resized
                    resize_corner = 2
                    resize_start = (left + clipboard.get_width(), top)
                    select_state = 6
                elif bottom_right_rect.collidepoint(mx, my): # bottom right being resized
                    resize_corner = 3
                    resize_start = (left, top)
                    select_state = 6

                # if the user clicks inside the selection rectangle, start moving the selection
                elif Rect(left, top, clipboard.get_width(), clipboard.get_height()).collidepoint(mx, my):
                    select_state = 4
                # if the user clicks outside the selection rectangle, finish the selection
                else:
                    select_state = 5
            elif mouse_up:
                select_state = 3
        case 4: # moving selection
            # if the user clicks outside the selection rectangle, finish the selection
            dx = dmx - move_start[0]
            dy = dmy - move_start[1]
            top = my - dy
            left = mx - dx
            width = clipboard.get_width()
            height = clipboard.get_height()

            if not Rect(left, top, width, height).collidepoint(mx, my): # outside the selection rectangle
                select_state = 5

            # if the user releases the mouse, go back to selected state with the new location
            if mouse_up:
                move_start = (left, top)
                select_state = 3
        case 5: # finished moving selection
            select_state = 0
            clipboard = None
        case 6: # resizing selection
            # if the user releases the mouse, go back to selected state with the new size
            if mouse_up:
                select_state = 7
        case 7:
            select_state = 3
    return select_state

def match_resize_corner(corner, resize_start, left, top, RHS):
    # match the corner and resize the selection rectangle
    if corner == 0: # top left
        top = min(top, resize_start[1] - RHS)
        left = min(left, resize_start[0] - RHS)
    elif corner == 1: # top right
        top = min(top, resize_start[1] - RHS)
        left = max(left, resize_start[0])
    elif corner == 2: # bottom left
        top = max(top, resize_start[1])
        left = min(left, resize_start[0] - RHS)
    elif corner == 3: # bottom right
        top = max(top, resize_start[1])
        left = max(left, resize_start[0])
    return left, top

def draw_resize_boxes(screen, rect, colour):
    left, top, width, height = rect
    RHS2 = RHS // 2

    # draw the resize boxes on the corners
    draw.rect(screen, colour, (left - RHS2, top - RHS2, RHS, RHS))
    draw.rect(screen, colour, (left + width - RHS2, top - RHS2, RHS, RHS))
    draw.rect(screen, colour, (left - RHS2, top + height - RHS2, RHS, RHS))
    draw.rect(screen, colour, (left + width - RHS2, top + height - RHS2, RHS, RHS))

def get_resize_rect(corner, resize_start, mx, my, dmx, dmy, clipboard):
    match corner: # calculate the new width and height based on the corner being resized
        case 0: # top left
            width = clipboard.get_width() + dmx - mx
            height = clipboard.get_height() + dmy - my
            left = resize_start[0] - width
            top = resize_start[1] - height
        case 1: # top right
            width = clipboard.get_width() - dmx + mx
            height = clipboard.get_height() + dmy - my
            left = resize_start[0]
            top = resize_start[1] - height
        case 2: # bottom left
            width = clipboard.get_width() + dmx - mx
            height = clipboard.get_height() - dmy + my
            left = resize_start[0] - width
            top = resize_start[1]
        case 3: # bottom right
            width = clipboard.get_width() - dmx + mx
            height = clipboard.get_height() - dmy + my
            left = resize_start[0]
            top = resize_start[1]
            
    # make sure the width and height are at least RHS pixels
    width = max(width, RHS)
    height = max(height, RHS)

    left, top = match_resize_corner(resize_corner, resize_start, left, top, RHS)
    return left, top, width, height
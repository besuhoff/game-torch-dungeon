import pygame, math

def line_intersects_rect(x1: float, y1: float, x2: float, y2: float, rx: float, ry: float, rw: float, rh: float):
        # Simple line-rectangle intersection check
        left = rx
        right = left + rw
        top = ry
        bottom = top + rh
        
        # Check if line is completely to one side of rectangle
        if max(x1, x2) < left or min(x1, x2) > right:
            return False
        if max(y1, y2) < top or min(y1, y2) > bottom:
            return False
            
        return True


def rotate_point(x1: float, y1: float, angle_degrees: float):
    radians = math.radians(angle_degrees)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    x_new = x1 * cosine + y1 * sine
    y_new = -x1 * sine + y1 * cosine
    return x_new, y_new

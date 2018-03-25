import pygame
from colors import Color

SELECTIVE_UPDATE_LIMIT = 1000

def draw_grid_to(surface, color_grid, block_size, changed=None):
    has_changed_supplied = changed is not None and isinstance(changed, list)
    if not has_changed_supplied:
        surface.fill(Color.BLACK)
        for i, row in enumerate(color_grid):
            for j, color in enumerate(row):
                y, x = i * block_size, j * block_size
                rect = pygame.rect.Rect(x, y, block_size, block_size)
                surface.fill(color, rect)
        return None
    else:
        rects = []
        for j, i in changed:
            color = color_grid[i][j]
            y, x = i * block_size, j * block_size
            rect = pygame.rect.Rect(x, y, block_size, block_size)
            surface.fill(color, rect)
            rects.append(rect)
        if len(rects) >= SELECTIVE_UPDATE_LIMIT:
            return None
        else:
            return rects

def draw_grid_to_cond(surface, array, block_size, changed=None):
    has_changed_supplied = changed is not None and isinstance(changed, list)
    if not has_changed_supplied:
        surface.fill(Color.BLACK)
        for i, row in enumerate(array):
            for j, elem in enumerate(row):
                y, x = i * block_size, j * block_size
                rect = pygame.rect.Rect(x, y, block_size, block_size)
                color = Color.WHITE if elem else Color.BLACK
                surface.fill(color, rect)
        return None
    else:
        rects = []
        for j, i in changed:
            elem = array[i][j]
            y, x = i * block_size, j * block_size
            rect = pygame.rect.Rect(x, y, block_size, block_size)
            color = Color.WHITE if elem else Color.BLACK
            surface.fill(color, rect)
            rects.append(rect)
        if len(rects) >= SELECTIVE_UPDATE_LIMIT:
            return None
        else:
            return rects

import pygame
import sys
import random
import time
from logic import solve_bfs, solve_dfs, solve_ids, solve_ida_star, solve_a_star

COLOR_FRAME = (90, 50, 50)
COLOR_TILE_BG = (255, 255, 255)
COLOR_EMPTY_BG = (160, 110, 80)
COLOR_TEXT = (0, 0, 0)
COLOR_BORDER = (0, 0, 0)
COLOR_APP_BG = (240, 240, 240)
WIDTH, HEIGHT = 500, 900 
GRID_SIZE, TILE_SIZE = 3, 120
FRAME_WIDTH, FRAME_RADIUS = 20, 15

class EightPuzzleGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("So sánh 5 Thuật Toán - 8-Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16, bold=True)
        
        self.goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        self.state = list(self.goal)
        self.message = "R: Shuffle | C: Compare All"
        self.running_algorithm = False
        
        self.stats = {
            "BFS": {"steps": 0, "nodes": 0}, 
            "DFS": {"steps": 0, "nodes": 0},
            "IDS": {"steps": 0, "nodes": 0},
            "IDA*": {"steps": 0, "nodes": 0},
            "A*": {"steps": 0, "nodes": 0}
        }

    def apply_move(self, action, state_to_mod):
        zero_idx = state_to_mod.index(0)
        row, col = zero_idx // 3, zero_idx % 3
        new_idx = zero_idx
        if action == "UP" and row > 0: new_idx = (row - 1) * 3 + col
        elif action == "DOWN" and row < 2: new_idx = (row + 1) * 3 + col
        elif action == "LEFT" and col > 0: new_idx = row * 3 + (col - 1)
        elif action == "RIGHT" and col < 2: new_idx = row * 3 + (col + 1)
        state_to_mod[zero_idx], state_to_mod[new_idx] = state_to_mod[new_idx], state_to_mod[zero_idx]

    def animate_solution(self, path, delay=300):
        for action in path:
            self.apply_move(action, self.state)
            self.draw_all()
            pygame.display.flip()
            pygame.time.delay(delay)

    def draw_puzzle(self):
        start_x = (WIDTH - (GRID_SIZE * TILE_SIZE + 2 * FRAME_WIDTH)) // 2
        start_y = 40
        total_size = GRID_SIZE * TILE_SIZE + 2 * FRAME_WIDTH
        pygame.draw.rect(self.screen, COLOR_FRAME, (start_x, start_y, total_size, total_size), border_radius=FRAME_RADIUS)
        for i, val in enumerate(self.state):
            row, col = i // GRID_SIZE, i % GRID_SIZE
            rect = pygame.Rect(start_x + FRAME_WIDTH + col * TILE_SIZE, start_y + FRAME_WIDTH + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if val != 0:
                pygame.draw.rect(self.screen, COLOR_TILE_BG, rect)
                text = self.font.render(str(val), True, COLOR_TEXT)
                self.screen.blit(text, text.get_rect(center=rect.center))
            else:
                pygame.draw.rect(self.screen, COLOR_EMPTY_BG, rect)
            pygame.draw.rect(self.screen, COLOR_BORDER, rect, 2)

    def draw_comparison_table(self):
        table_y = HEIGHT - 300
        headers = ["Algorithm", "Steps", "Nodes Explored"]
        for i, h in enumerate(headers):
            text = self.small_font.render(h, True, (0, 0, 0))
            self.screen.blit(text, (40 + i*150, table_y))
        
        list_algo = [
            ("BFS", "BFS", (0, 100, 0)),
            ("DFS (Lim 20)", "DFS", (150, 0, 0)),
            ("IDS", "IDS", (0, 0, 150)),
            ("IDA*", "IDA*", (150, 100, 0)),
            ("A*", "A*", (100, 0, 150))
        ]
        
        for idx, (label, key, color) in enumerate(list_algo):
            data = [label, str(self.stats[key]["steps"]), str(self.stats[key]["nodes"])]
            for i, d in enumerate(data):
                text = self.small_font.render(d, True, color)
                self.screen.blit(text, (40 + i*150, table_y + 35 + idx*35))

    def draw_all(self):
        self.screen.fill(COLOR_APP_BG)
        self.draw_puzzle()
        msg_surf = self.small_font.render(self.message, True, (50, 50, 50))
        self.screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 330)))
        self.draw_comparison_table()

    def run(self):
        while True:
            self.draw_all()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and not self.running_algorithm:
                    if event.key == pygame.K_r:
                        self.state = list(self.goal)
                        for _ in range(15):
                            zero_idx = self.state.index(0)
                            moves = []
                            row, col = zero_idx // 3, zero_idx % 3
                            if row > 0: moves.append("UP")
                            if row < 2: moves.append("DOWN")
                            if col > 0: moves.append("LEFT")
                            if col < 2: moves.append("RIGHT")
                            self.apply_move(random.choice(moves), self.state)
                        self.message = "Puzzle Ready! Press C to Compare."
                    
                    elif event.key == pygame.K_c:
                        self.running_algorithm = True
                        original_start = list(self.state)
                        
                        algos = [
                            ("BFS", solve_bfs, {}),
                            ("DFS", solve_dfs, {"limit": 20}),
                            ("IDS", solve_ids, {"max_depth": 20}),
                            ("IDA*", solve_ida_star, {}),
                            ("A*", solve_a_star, {})
                        ]
                        
                        for name, func, kwargs in algos:
                            self.message = f"Solving with {name}..."
                            self.draw_all(); pygame.display.flip()
                            path, nodes = func(original_start, self.goal, **kwargs)
                            self.stats[name] = {"steps": len(path) if path else "X", "nodes": nodes}
                        
                        path_a, _ = solve_a_star(original_start, self.goal)
                        if path_a:
                            self.message = "Showing A* Solution..."
                            self.animate_solution(path_a)
                        
                        self.message = "Done! Press R to shuffle again."
                        self.running_algorithm = False

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    EightPuzzleGUI().run()
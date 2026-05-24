import heapq
from collections import deque

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = tuple(state) # Chuyển về tuple để có thể hash được
        self.parent = parent
        self.action = action

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return self.state == other.state

    def __lt__(self, other):
        return False

def get_neighbors(state):
    neighbors = []
    state_list = list(state)
    zero_idx = state_list.index(0)
    row, col = zero_idx // 3, zero_idx % 3
    
    # Định nghĩa di chuyển ô trống: (row_change, col_change, action_name)
    moves = [(-1, 0, "UP"), (1, 0, "DOWN"), (0, -1, "LEFT"), (0, 1, "RIGHT")]
    
    for dr, dc, action in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_idx = new_row * 3 + new_col
            new_state = state_list[:]
            new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
            neighbors.append(Node(new_state, None, action))
    return neighbors

def solve_bfs(start_state, goal_state):
    start_node = Node(start_state)
    goal_node = Node(goal_state)
    
    queue = deque([start_node])
    visited = {start_node.state}
    nodes_explored = 0
    
    while queue:
        current_node = queue.popleft()
        nodes_explored += 1
        
        if current_node.state == goal_node.state:
            return construct_path(current_node), nodes_explored
            
        for neighbor in get_neighbors(current_node.state):
            if neighbor.state not in visited:
                visited.add(neighbor.state)
                neighbor.parent = current_node # Gán cha để truy vết
                queue.append(neighbor)
    return None, nodes_explored

def solve_dfs(start_state, goal_state, limit=500):
    # DFS thuần túy rất dễ treo, ở đây dùng phiên bản giới hạn độ sâu (DLS)
    start_node = Node(start_state)
    stack = [(start_node, 0)] # (node, depth)
    visited = {} # Lưu trạng thái và độ sâu tối thiểu tìm thấy nó
    nodes_explored = 0
    
    while stack:
        current_node, depth = stack.pop()
        nodes_explored += 1
        
        if current_node.state == tuple(goal_state):
            return construct_path(current_node), nodes_explored
        
        if depth < limit:
            if current_node.state not in visited or visited[current_node.state] > depth:
                visited[current_node.state] = depth
                for neighbor in get_neighbors(current_node.state):
                    neighbor.parent = current_node
                    stack.append((neighbor, depth + 1))
    return None, nodes_explored

def construct_path(node):
    path = []
    while node.parent is not None:
        path.append(node.action)
        node = node.parent
    return path[::-1] # Đảo ngược để có Đầu -> Đích

# Thêm hàm Heuristic tính khoảng cách Manhattan cho IDA*
def manhattan_distance(state, goal_state):
    dist = 0
    # Chuyển state (tuple) và goal_state (list/tuple) về list để dễ index
    state_list = list(state)
    goal_list = list(goal_state)
    
    for i in range(9):
        if state_list[i] == 0:
            continue
        goal_idx = goal_list.index(state_list[i])
        dist += abs((i // 3) - (goal_idx // 3)) + abs((i % 3) - (goal_idx % 3))
    return dist

# Thuật toán IDS (Iterative Deepening Search)
def solve_ids(start_state, goal_state, max_depth=50):
    start_node = Node(start_state)
    goal_tuple = tuple(goal_state)
    total_nodes = 0

    def dls(current_node, depth, path_states):
        nonlocal total_nodes
        total_nodes += 1

        if current_node.state == goal_tuple:
            return construct_path(current_node)
        
        if depth == 0:
            return None
            
        for neighbor in get_neighbors(current_node.state):
            # Kiểm tra tránh lặp lại trạng thái trong cùng một nhánh (tránh chu trình)
            if neighbor.state not in path_states:
                neighbor.parent = current_node
                path_states.add(neighbor.state)
                
                result = dls(neighbor, depth - 1, path_states)
                if result is not None:
                    return result
                    
                # Backtrack
                path_states.remove(neighbor.state)
                
        return None

    # Tăng dần độ sâu
    for depth in range(max_depth):
        result = dls(start_node, depth, {start_node.state})
        if result is not None:
            return result, total_nodes
            
    return None, total_nodes

# Thuật toán IDA* (Iterative Deepening A*)
def solve_ida_star(start_state, goal_state):
    start_node = Node(start_state)
    goal_tuple = tuple(goal_state)
    total_nodes = 0
    
    # Ngưỡng ban đầu là khoảng cách Manhattan từ trạng thái bắt đầu đến đích
    threshold = manhattan_distance(start_node.state, goal_tuple)
    
    def search(current_node, g, bound, path_states):
        nonlocal total_nodes
        total_nodes += 1
        
        # f(n) = g(n) + h(n)
        f = g + manhattan_distance(current_node.state, goal_tuple)
        
        if f > bound:
            return f, None
        if current_node.state == goal_tuple:
            return "FOUND", construct_path(current_node)
            
        min_bound = float('inf')
        
        for neighbor in get_neighbors(current_node.state):
            if neighbor.state not in path_states:
                neighbor.parent = current_node
                path_states.add(neighbor.state)
                
                # Gọi đệ quy với g tăng lên 1 (chi phí mỗi bước di chuyển là 1)
                t, result_path = search(neighbor, g + 1, bound, path_states)
                
                if t == "FOUND":
                    return "FOUND", result_path
                if t < min_bound:
                    min_bound = t
                    
                # Backtrack
                path_states.remove(neighbor.state)
                
        return min_bound, None

    # Lặp với ngưỡng tăng dần
    while True:
        t, result_path = search(start_node, 0, threshold, {start_node.state})
        if t == "FOUND":
            return result_path, total_nodes
        if t == float('inf'):
            return None, total_nodes
            
        # Cập nhật ngưỡng mới là giá trị f nhỏ nhất bị vượt quá
        threshold = t

# Thuật toán A* (A Star)
def solve_a_star(start_state, goal_state):
    start_node = Node(start_state)
    goal_tuple = tuple(goal_state)
    h_start = manhattan_distance(start_node.state, goal_tuple)
    pq = [(h_start, 0, start_node)]
    visited = {tuple(start_state): 0}
    nodes_explored = 0

    while pq:
        f, g, current_node = heapq.heappop(pq)
        nodes_explored += 1
        if current_node.state == goal_tuple:
            return construct_path(current_node), nodes_explored
        for neighbor in get_neighbors(current_node.state):
            new_g = g + 1
            state_tuple = neighbor.state
            if state_tuple not in visited or new_g < visited[state_tuple]:
                visited[state_tuple] = new_g
                neighbor.parent = current_node
                h = manhattan_distance(state_tuple, goal_tuple)
                heapq.heappush(pq, (new_g + h, new_g, neighbor))
    return None, nodes_explored
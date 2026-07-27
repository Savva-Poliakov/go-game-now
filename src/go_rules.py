class GoBoard:
    def __init__(self, size=19):
        self.size = size
        self.board = [[None] * size for _ in range(size)]
        self.current_player = 'black'
        self.previous_board_state = None
        self.captures = {'black': 0, 'white': 0}
        self.passes = 0
        self.game_over = False

    def in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def neighbors(self, x, y):
        result = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                result.append((nx, ny))
        return result

    def opponent(self, color):
        return 'white' if color == 'black' else 'black'

    def get_group(self, x, y):
        color = self.board[y][x]
        if color is None:
            return set(), set()
        visited = set()
        stack = [(x, y)]
        stones = set()
        liberties = set()
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            stones.add((cx, cy))
            for nx, ny in self.neighbors(cx, cy):
                ncolor = self.board[ny][nx]
                if ncolor is None:
                    liberties.add((nx, ny))
                elif ncolor == color and (nx, ny) not in visited:
                    stack.append((nx, ny))
        return stones, liberties

    def board_snapshot(self):
        return tuple(tuple(row) for row in self.board)

    def is_legal_move(self, x, y, color):
        if not self.in_bounds(x, y):
            return False
        if self.board[y][x] is not None:
            return False
        self.board[y][x] = color
        opp_color = self.opponent(color)
        captured = []
        for nx, ny in self.neighbors(x, y):
            if self.board[ny][nx] == opp_color:
                stones, liberties = self.get_group(nx, ny)
                if len(liberties) == 0:
                    captured.append(stones)
        own_stones, own_liberties = self.get_group(x, y)
        legal = True
        if len(own_liberties) == 0 and not captured:
            legal = False
        if legal and captured:
            temp_board = [row[:] for row in self.board]
            for group in captured:
                for (gx, gy) in group:
                    temp_board[gy][gx] = None
            snapshot = tuple(tuple(row) for row in temp_board)
            if snapshot == self.previous_board_state:
                legal = False
        self.board[y][x] = None
        return legal

    def play_move(self, x, y, color):
        if color != self.current_player:
            return False
        if not self.is_legal_move(x, y, color):
            return False
        pre_move_state = self.board_snapshot()
        self.board[y][x] = color
        opp_color = self.opponent(color)
        captured_stones = []
        for nx, ny in self.neighbors(x, y):
            if self.board[ny][nx] == opp_color:
                stones, liberties = self.get_group(nx, ny)
                if len(liberties) == 0:
                    captured_stones.extend(stones)
        for (gx, gy) in captured_stones:
            self.board[gy][gx] = None
        self.captures[color] += len(captured_stones)
        self.previous_board_state = pre_move_state
        self.passes = 0
        self.current_player = opp_color
        return True

    def pass_turn(self):
        self.passes += 1
        self.current_player = self.opponent(self.current_player)
        if self.passes >= 2:
            self.game_over = True

    def resign(self, color):
        self.game_over = True
        return self.opponent(color)

    def get_legal_moves(self, color):
        moves = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] is None and self.is_legal_move(x, y, color):
                    moves.append((x, y))
        return moves

    def calculate_territory(self):
        visited = set()
        territory = {'black': 0, 'white': 0}
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] is None and (x, y) not in visited:
                    stack = [(x, y)]
                    region = set()
                    border_colors = set()
                    while stack:
                        cx, cy = stack.pop()
                        if (cx, cy) in visited:
                            continue
                        visited.add((cx, cy))
                        region.add((cx, cy))
                        for nx, ny in self.neighbors(cx, cy):
                            ncolor = self.board[ny][nx]
                            if ncolor is None and (nx, ny) not in visited:
                                stack.append((nx, ny))
                            elif ncolor is not None:
                                border_colors.add(ncolor)
                    if len(border_colors) == 1:
                        owner = border_colors.pop()
                        territory[owner] += len(region)
        return territory

    def calculate_score(self):
        territory = self.calculate_territory()
        stones = {'black': 0, 'white': 0}
        for row in self.board:
            for cell in row:
                if cell is not None:
                    stones[cell] += 1
        return {
            'black': stones['black'] + territory['black'],
            'white': stones['white'] + territory['white']
        }

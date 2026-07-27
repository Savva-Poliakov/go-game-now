import random
from go_rules import GoBoard


def build_levels():
    ranks = [f"{k}k" for k in range(20, 0, -1)] + [f"{d}d" for d in range(1, 10)]
    levels = {}
    max_strength = len(ranks) - 1
    for strength, rank in enumerate(ranks):
        ratio = strength / max_strength
        random_chance = max(0.0, 0.55 - ratio * 0.55)
        precision = 0.15 + ratio * 0.85
        candidate_pool = 4 + int(ratio * 10)
        depth = 0
        if ratio > 0.45:
            depth = 1
        if ratio > 0.8:
            depth = 2
        levels[rank] = {
            'random_chance': random_chance,
            'precision': precision,
            'candidate_pool': candidate_pool,
            'depth': depth
        }
    return levels


LEVELS = build_levels()


def list_levels():
    return list(LEVELS.keys())


class GoEngine:
    def __init__(self, level):
        if level not in LEVELS:
            raise ValueError(f"Unknown level: {level}")
        self.level = level
        self.config = LEVELS[level]

    def choose_move(self, board, color):
        moves = board.get_legal_moves(color)
        if not moves:
            return None
        if random.random() < self.config['random_chance']:
            return random.choice(moves)
        ranked = self.rank_moves_by_heuristic(board, moves, color)
        pool_size = min(len(ranked), self.config['candidate_pool'])
        candidates = ranked[:pool_size]
        if self.config['depth'] == 0:
            scored = candidates
        else:
            scored = []
            for move, _ in candidates:
                value = self.minimax_value(board, move, color, self.config['depth'])
                scored.append((move, value))
            scored.sort(key=lambda item: item[1], reverse=True)
        top_n = max(1, int(len(scored) * self.config['precision']))
        return random.choice(scored[:top_n])[0]

    def rank_moves_by_heuristic(self, board, moves, color):
        scored = [(move, self.heuristic_score(board, move, color)) for move in moves]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored

    def heuristic_score(self, board, move, color):
        x, y = move
        opp = board.opponent(color)
        score = 0.0
        for nx, ny in board.neighbors(x, y):
            if board.board[ny][nx] == opp:
                stones, liberties = board.get_group(nx, ny)
                if len(liberties) == 1:
                    score += len(stones) * 5
        clone = self.clone_board(board)
        clone.play_move(x, y, color)
        own_stones, own_liberties = clone.get_group(x, y)
        if len(own_liberties) == 0:
            score -= 100
        elif len(own_liberties) == 1:
            score -= 8
        score += len(own_liberties) * 0.5
        center = board.size / 2
        dist = abs(x - center) + abs(y - center)
        score += max(0, board.size - dist) * 0.05
        return score

    def clone_board(self, board):
        clone = GoBoard(board.size)
        clone.board = [row[:] for row in board.board]
        clone.current_player = board.current_player
        clone.previous_board_state = board.previous_board_state
        clone.captures = dict(board.captures)
        clone.passes = board.passes
        clone.game_over = board.game_over
        return clone

    def minimax_value(self, board, move, color, depth):
        clone = self.clone_board(board)
        x, y = move
        clone.play_move(x, y, color)
        return self.minimax(clone, board.opponent(color), color, depth - 1)

    def minimax(self, board, to_move, root_color, depth):
        if depth == 0 or board.game_over:
            return self.position_score(board, root_color)
        moves = board.get_legal_moves(to_move)
        if not moves:
            return self.position_score(board, root_color)
        candidates = self.rank_moves_by_heuristic(board, moves, to_move)[:6]
        values = []
        for candidate_move, _ in candidates:
            clone = self.clone_board(board)
            clone.play_move(candidate_move[0], candidate_move[1], to_move)
            values.append(self.minimax(clone, board.opponent(to_move), root_color, depth - 1))
        if to_move == root_color:
            return max(values)
        return min(values)

    def position_score(self, board, color):
        score = board.calculate_score()
        opp = board.opponent(color)
        return score[color] - score[opp]

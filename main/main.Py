import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions and constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)  # Color for highlighting available moves

# Load Chess pieces
PIECES = {
    "w_king": pygame.image.load("assets/photo 6.jpg"),
    "w_queen": pygame.image.load("assets/photo 10.jpg"),
    "w_rook": pygame.image.load("assets/photo 8.jpg"),
    "w_bishop": pygame.image.load("assets/photo 12.jpg"),
    "w_knight": pygame.image.load("assets/photo 2.jpg"),
    "w_pawn": pygame.image.load("assets/photo 4.jpg"),
    "b_king": pygame.image.load("assets/photo 9.jpg"),
    "b_queen": pygame.image.load("assets/photo 7.jpg"),
    "b_rook": pygame.image.load("assets/photo 11.jpg"),
    "b_bishop": pygame.image.load("assets/photo 5.jpg"),
    "b_knight": pygame.image.load("assets/photo 3.jpg"),
    "b_pawn": pygame.image.load("assets/photo 1.jpg"),
}

# Resize images to fit squares
for key in PIECES:
    PIECES[key] = pygame.transform.scale(PIECES[key], (SQUARE_SIZE, SQUARE_SIZE))

# Load move sound
MOVE_SOUND = pygame.mixer.Sound("main/move.wav")

# Chessboard starting position
STARTING_POSITION = [
    ["b_rook", "b_knight", "b_bishop", "b_queen", "b_king", "b_bishop", "b_knight", "b_rook"],
    ["b_pawn"] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    ["w_pawn"] * 8,
    ["w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "w_bishop", "w_knight", "w_rook"],
]

# Draw the chessboard
def draw_board(screen, valid_moves, capture_moves):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            if (row, col) in valid_moves:
                color = HIGHLIGHT_COLOR
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Draw a circle around capturable pieces
            if (row, col) in capture_moves:
                pygame.draw.circle(screen, (255, 0, 0), (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 4)

# Draw pieces on the board
def draw_pieces(screen, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                screen.blit(PIECES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Validate moves for all pieces
def is_valid_move(piece, start, end, board):
    piece_type = piece[2:]  # "pawn", "rook", etc.
    piece_color = piece[0]  # "w" or "b"
    start_row, start_col = start
    end_row, end_col = end

    # Prevent capturing own pieces
    if board[end_row][end_col] and board[end_row][end_col][0] == piece_color:
        return False

    if piece_type == "pawn":
        direction = -1 if piece_color == "w" else 1
        if start_col == end_col:  # Forward move
            if board[end_row][end_col] is None:
                if end_row == start_row + direction:
                    return True
                if end_row == start_row + 2 * direction and (start_row == 6 if piece_color == "w" else start_row == 1):
                    return True
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:  # Capture move
            if board[end_row][end_col]:
                return True
    elif piece_type == "rook":
        if start_row == end_row or start_col == end_col:  # Horizontal or vertical
            step_row = (end_row - start_row) // max(1, abs(end_row - start_row)) if start_row != end_row else 0
            step_col = (end_col - start_col) // max(1, abs(end_col - start_col)) if start_col != end_col else 0

            current_row, current_col = start_row + step_row, start_col + step_col
            while (current_row, current_col) != (end_row, end_col):
                if board[current_row][current_col]:
                    return False
                current_row += step_row
                current_col += step_col
            return True
    elif piece_type == "knight":
        if (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]:
            return True
    elif piece_type == "bishop":
        if abs(start_row - end_row) == abs(start_col - end_col):  # Diagonal
            step_row = (end_row - start_row) // abs(end_row - start_row)
            step_col = (end_col - start_col) // abs(end_col - start_col)

            current_row, current_col = start_row + step_row, start_col + step_col
            while (current_row, current_col) != (end_row, end_col):
                if board[current_row][current_col]:
                    return False
                current_row += step_row
                current_col += step_col
            return True
    elif piece_type == "queen":
        # Combines rook and bishop movement
        return is_valid_move(piece_color + "_rook", start, end, board) or is_valid_move(piece_color + "_bishop", start, end, board)
    elif piece_type == "king":
        if max(abs(start_row - end_row), abs(start_col - end_col)) == 1:
            return True

    return False

# Get all valid moves for a selected piece
def get_valid_moves(piece, start, board):
    valid_moves = []
    capture_moves = []  # To store capture moves
    for row in range(ROWS):
        for col in range(COLS):
            if is_valid_move(piece, start, (row, col), board):
                valid_moves.append((row, col))
                if board[row][col] and board[row][col][0] != piece[0]:  # Check if it's a capturable piece
                    capture_moves.append((row, col))
    return valid_moves, capture_moves

# End the game when the king is captured
def check_for_king_capture(board):
    white_king_present = any("w_king" in row for row in board)
    black_king_present = any("b_king" in row for row in board)

    if not white_king_present:
        print("Black wins! White's king has been captured.")
        pygame.quit()
        sys.exit()
    if not black_king_present:
        print("White wins! Black's king has been captured.")
        pygame.quit()
        sys.exit()

# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")

    board = [row[:] for row in STARTING_POSITION]
    selected_piece = None
    valid_moves = []
    capture_moves = []  # Store capture moves here
    running = True
    turn = "w"  # "w" for white, "b" for black

    while running:
        draw_board(screen, valid_moves, capture_moves)
        draw_pieces(screen, board)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row, col = y // SQUARE_SIZE, x // SQUARE_SIZE

                if selected_piece:
                    if (row, col) in valid_moves:
                        board[selected_piece[1]][selected_piece[2]] = None
                        board[row][col] = selected_piece[0]
                        MOVE_SOUND.play()  # Play the sound effect
                        turn = "b" if turn == "w" else "w"  # Switch turn
                        check_for_king_capture(board)  # Check after every move
                    selected_piece = None
                    valid_moves = []
                    capture_moves = []  # Reset capture moves
                else:
                    if board[row][col] and board[row][col][0] == turn:
                        selected_piece = (board[row][col], row, col)
                        valid_moves, capture_moves = get_valid_moves(selected_piece[0], (row, col), board)  # Get both valid and capture moves

# Run the game
if __name__ == "__main__":
    main()
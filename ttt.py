class Field:
    def __init__(self) -> None:
        self.content = ([None, None, None], [None, None, None], [None, None, None])
        self.next = 'X'
        self.moves = []

    def move(self, x: int, y: int):
        if self.content[x][y] is not None: raise AttributeError("Incorrect move")
        self.content[x][y] = self.next
        self.moves.append(f"{self.next}{x}{y}")

        self.next = 'O' if self.next == 'X' else 'X'

    def __str__(self) -> str:
        c = self.content
        out_str = f"{c[0][0] or '.'}|{c[1][0] or '.'}|{c[2][0] or '.'}\n"
        out_str += "-+-+-\n"
        out_str += f"{c[0][1] or '.'}|{c[1][1] or '.'}|{c[2][1] or '.'}\n"
        out_str += "-+-+-\n"
        out_str += f"{c[0][2] or '.'}|{c[1][2] or '.'}|{c[2][2] or '.'}"
        return out_str

    def get_cell(self, x: int, y: int) -> str:
        return self.content[x][y]

    def check_win(self):
        check = lambda args: all([el == args[i-1] for i, el in enumerate(args[1:])]) and all(args)
        check_row = lambda cont, col: check([cont[row][col] for row in range(3)])
        check_col = lambda cont, row: check(cont[row])
        check_m_diag = lambda cont: check([cont[i][i] for i in range(3)])
        check_s_diag = lambda cont: check([cont[i][2-i] for i in range(3)])


        return (*[check_row(self.content, i) for i in range(3)],
                   *[check_col(self.content, i) for i in range(3)],
                   check_m_diag(self.content),
                   check_s_diag(self.content),
                all(sum(self.content, []))
                ), None
    @classmethod
    def set_moves(cls, moves: str):
        new_field = cls()
        try:
            moves = moves.split(', ')
            for move in moves:
                who, x, y = move
                if new_field.next == who:
                    new_field.move(int(x), int(y))
        except: ...
        return new_field

if __name__ == "__main__":
    f = Field()

    while not f.check_win():
        print("[2J", end="[H")
        print(f)
        print("Moves: ", ", ".join(f.moves))
        print()
        x, y = map(int, input('> ').split())
        f.move(x, y)
    print("[2J", end="[H")
    print("Moves: ", ", ".join(f.moves))
    print(f)


"""
Game of Life — Three-Way Glider Wars
سه تیم: آبی (از چپ)، قرمز (از راست)، سبز (از پایین)
"""
import tkinter as tk
import random

# ---------- تنظیمات ----------
CELL  = 9
COLS  = 90
ROWS  = 60
DELAY = 70

BG = "#0a0c15"

NONE, BLUE, RED, GREEN, CONTESTED = 0, 1, 2, 3, 4
MAX_AGE = 6
TEAMS = [BLUE, RED, GREEN]

# ---------- رنگ‌ها ----------
LIVE = {
    BLUE:      ["#c0eaff", "#80d0ff", "#40a8ff", "#2080e0",
                "#155ab0", "#0e3a7a", "#082850"],
    RED:       ["#ffc0d0", "#ff8098", "#ff5070", "#d03050",
                "#a02038", "#701525", "#4a0d18"],
    GREEN:     ["#c0ffd0", "#80ffa0", "#40ff70", "#20d050",
                "#15a038", "#0e7025", "#084a18"],
    CONTESTED: ["#ffe0a0", "#ffc860", "#ffa830", "#d08020",
                "#a06018", "#704010", "#402a08"],
}
DEAD = {
    BLUE:      "#0a1020",
    RED:       "#200a10",
    GREEN:     "#0a2010",
    CONTESTED: "#201810",
    NONE:      BG,
}

# ---------- الگوی گلایدر در ۴ جهت ----------
GLIDERS = {
    "SE": [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],  # ↓→
    "SW": [(1, 0), (0, 1), (0, 2), (1, 2), (2, 2)],  # ↓←
    "NE": [(0, 0), (1, 0), (2, 0), (2, 1), (1, 2)],  # ↑→
    "NW": [(0, 0), (1, 0), (2, 0), (0, 1), (1, 2)],  # ↑←
}

# جهت‌های هر تیم
TEAM_DIRS = {
    BLUE:  ["NE", "SE"],   # از چپ → راست
    RED:   ["NW", "SW"],   # از راست → چپ
    GREEN: ["NE", "NW"],   # از پایین → بالا
}


# =====================================================================
#  منطق بازی
# =====================================================================
class GameOfWar:
    def __init__(self):
        self.alive = [[0] * COLS for _ in range(ROWS)]
        self.team  = [[NONE] * COLS for _ in range(ROWS)]
        self.age   = [[0] * COLS for _ in range(ROWS)]
        self.gen = 0
        self.paused = False
        self.auto_war = True
        self.spawn_interval = 15

        # جای‌گذاری اولیه — ۲ گلایدر از هر تیم
        # آبی از چپ
        self.place_glider(5, ROWS // 3, BLUE, "NE")
        self.place_glider(5, 2 * ROWS // 3, BLUE, "SE")
        # قرمز از راست
        self.place_glider(COLS - 8, ROWS // 3, RED, "NW")
        self.place_glider(COLS - 8, 2 * ROWS // 3, RED, "SW")
        # سبز از پایین
        self.place_glider(COLS // 3, ROWS - 8, GREEN, "NW")
        self.place_glider(2 * COLS // 3, ROWS - 8, GREEN, "NE")

    def place_glider(self, x, y, team, direction):
        for dx, dy in GLIDERS[direction]:
            ny, nx = (y + dy) % ROWS, (x + dx) % COLS
            self.alive[ny][nx] = 1
            self.team[ny][nx]  = team
            self.age[ny][nx]   = 0

    def try_place_glider(self, x, y, team, direction):
        for dx, dy in GLIDERS[direction]:
            ny, nx = (y + dy) % ROWS, (x + dx) % COLS
            if self.alive[ny][nx]:
                return False
        self.place_glider(x, y, team, direction)
        return True

    def step(self):
        new_alive = [[0] * COLS for _ in range(ROWS)]
        new_team  = [row[:] for row in self.team]    # زمین حفظ می‌شود
        new_age   = [[0] * COLS for _ in range(ROWS)]

        for y in range(ROWS):
            for x in range(COLS):
                n = 0
                b = r = g = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = (y + dy) % ROWS, (x + dx) % COLS
                        if self.alive[ny][nx]:
                            n += 1
                            t = self.team[ny][nx]
                            if t == BLUE:       b += 1
                            elif t == RED:      r += 1
                            elif t == GREEN:    g += 1
                            # CONTESTED شمرده نمی‌شود

                if self.alive[y][x]:
                    if n in (2, 3):
                        new_alive[y][x] = 1
                        new_age[y][x] = min(self.age[y][x] + 1, MAX_AGE)
                    # مرگ → team حفظ می‌شود (زمین)
                else:
                    if n == 3:
                        new_alive[y][x] = 1
                        new_age[y][x] = 0
                        # کدام تیم برنده است؟
                        if b > r and b > g:
                            new_team[y][x] = BLUE
                        elif r > b and r > g:
                            new_team[y][x] = RED
                        elif g > b and g > r:
                            new_team[y][x] = GREEN
                        else:
                            # تساوی بین ۲ یا ۳ تیم
                            new_team[y][x] = CONTESTED

        self.alive, self.team, self.age = new_alive, new_team, new_age
        self.gen += 1

        # حمله‌ی خودکار
        if self.auto_war and self.gen % self.spawn_interval == 0:
            # آبی از چپ
            for _ in range(2):
                bx = random.randint(1, 12)
                by = random.randint(1, ROWS - 4)
                if self.try_place_glider(bx, by, BLUE,
                                          random.choice(TEAM_DIRS[BLUE])):
                    break
            # قرمز از راست
            for _ in range(2):
                rx = random.randint(COLS - 14, COLS - 4)
                ry = random.randint(1, ROWS - 4)
                if self.try_place_glider(rx, ry, RED,
                                          random.choice(TEAM_DIRS[RED])):
                    break
            # سبز از پایین
            for _ in range(2):
                gx = random.randint(1, COLS - 4)
                gy = random.randint(ROWS - 8, ROWS - 4)
                if self.try_place_glider(gx, gy, GREEN,
                                          random.choice(TEAM_DIRS[GREEN])):
                    break

    def scores(self):
        """برمی‌گرداند: live، territory برای هر ۳ تیم"""
        b_live = r_live = g_live = 0
        b_terr = r_terr = g_terr = 0
        for y in range(ROWS):
            for x in range(COLS):
                t = self.team[y][x]
                alive = self.alive[y][x]
                if t == BLUE:
                    b_terr += 1
                    if alive: b_live += 1
                elif t == RED:
                    r_terr += 1
                    if alive: r_live += 1
                elif t == GREEN:
                    g_terr += 1
                    if alive: g_live += 1
        return (b_live, r_live, g_live, b_terr, r_terr, g_terr)


# =====================================================================
#  GUI
# =====================================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("Game of Life — Three-Way Glider Wars")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.canvas = tk.Canvas(
            root, width=COLS * CELL, height=ROWS * CELL,
            bg=BG, highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(10, 4))

        # راهنمای رنگ‌ها
        legend = tk.Frame(root, bg=BG)
        legend.pack(fill="x", padx=12, pady=(0, 2))
        for name, color in [
            ("Blue (left →)",  LIVE[BLUE][2]),
            ("Red (right ←)",  LIVE[RED][2]),
            ("Green (bottom ↑)", LIVE[GREEN][2]),
            ("Contested",      LIVE[CONTESTED][2]),
        ]:
            box = tk.Frame(legend, bg=color, width=14, height=14)
            box.pack(side="left", padx=(0, 3), pady=2)
            tk.Label(legend, text=name, bg=BG, fg="#8fa3c8",
                     font=("Consolas", 9)).pack(side="left", padx=(0, 14))

        # خط وضعیت
        self.status = tk.Label(
            root, bg=BG, fg="#a0b8d8", font=("Consolas", 11), anchor="w",
        )
        self.status.pack(fill="x", padx=12, pady=(2, 2))

        # ردیف امتیاز — ۳ تیم + حکم
        score_row = tk.Frame(root, bg=BG)
        score_row.pack(fill="x", padx=12, pady=(0, 4))

        self.blue_score = tk.Label(
            score_row, bg=BG, fg="#60c8ff",
            font=("Consolas", 11, "bold"),
        )
        self.blue_score.pack(side="left", padx=(0, 18))

        self.red_score = tk.Label(
            score_row, bg=BG, fg="#ff7090",
            font=("Consolas", 11, "bold"),
        )
        self.red_score.pack(side="left", padx=(0, 18))

        self.green_score = tk.Label(
            score_row, bg=BG, fg="#60ff80",
            font=("Consolas", 11, "bold"),
        )
        self.green_score.pack(side="left", padx=(0, 18))

        self.verdict = tk.Label(
            score_row, bg=BG, fg="#ffd23c",
            font=("Consolas", 11, "bold"),
        )
        self.verdict.pack(side="left")

        # کنترل‌ها
        self.controls = tk.Label(
            root, bg=BG, fg="#7a8aaa",
            font=("Consolas", 9), anchor="w",
        )
        self.controls.pack(fill="x", padx=12, pady=(0, 8))

        # مستطیل‌ها
        self.rects = []
        for y in range(ROWS):
            row = []
            for x in range(COLS):
                r = self.canvas.create_rectangle(
                    x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL,
                    fill=BG, outline="",
                )
                row.append(r)
            self.rects.append(row)
        self.shown = [[BG] * COLS for _ in range(ROWS)]

        self.game = GameOfWar()
        self.delay = DELAY

        # کلیدها
        root.bind("<space>", lambda e: self.toggle_pause())
        root.bind("<n>",     lambda e: self.single_step())
        root.bind("<r>",     lambda e: self.reset())
        root.bind("<a>",     lambda e: self.toggle_auto())
        root.bind("<Up>",    lambda e: self.speed(-20))
        root.bind("<Down>",  lambda e: self.speed(20))
        root.bind("<Escape>", lambda e: root.destroy())

        # کلیک: چپ=آبی، وسط=سبز، راست=قرمز
        self.canvas.bind("<Button-1>", lambda e: self.click(e, BLUE))
        self.canvas.bind("<Button-2>", lambda e: self.click(e, GREEN))
        self.canvas.bind("<Button-3>", lambda e: self.click(e, RED))

        self.draw()
        self.loop()

    # ---------- کنترل ----------
    def click(self, event, team):
        x = event.x // CELL
        y = event.y // CELL
        d = random.choice(TEAM_DIRS[team])
        self.game.place_glider(x - 1, y - 1, team, d)
        self.draw()

    def toggle_pause(self):
        self.game.paused = not self.game.paused
        self.draw()

    def toggle_auto(self):
        self.game.auto_war = not self.game.auto_war
        self.draw()

    def single_step(self):
        self.game.paused = True
        self.game.step()
        self.draw()

    def speed(self, d):
        self.delay = max(20, min(500, self.delay + d))
        self.draw()

    def reset(self):
        self.game = GameOfWar()
        self.draw()

    # ---------- رسم ----------
    def draw(self):
        g = self.game
        for y in range(ROWS):
            for x in range(COLS):
                if g.alive[y][x]:
                    t = g.team[y][x]
                    a = min(g.age[y][x], len(LIVE[t]) - 1)
                    color = LIVE[t][a]
                else:
                    color = DEAD[g.team[y][x]]

                if self.shown[y][x] != color:
                    self.canvas.itemconfig(self.rects[y][x], fill=color)
                    self.shown[y][x] = color

        b_live, r_live, g_live, b_terr, r_terr, g_terr = g.scores()
        total = b_terr + r_terr + g_terr
        total = total if total else 1

        state = "PAUSED" if g.paused else "RUNNING"
        auto  = "ON" if g.auto_war else "OFF"
        self.status.config(
            text=f"Gen {g.gen:>4}  |  {state}  |  Auto-war: {auto}  |  Speed: {self.delay}ms"
        )

        self.blue_score.config(
            text=f"BLUE   {b_live:>3} live  {100*b_terr/total:>4.1f}%"
        )
        self.red_score.config(
            text=f"RED    {r_live:>3} live  {100*r_terr/total:>4.1f}%"
        )
        self.green_score.config(
            text=f"GREEN  {g_live:>3} live  {100*g_terr/total:>4.1f}%"
        )

        # حکم: چه کسی پیش است؟
        stats = [
            ("BLUE",  b_terr, "#60c8ff"),
            ("RED",   r_terr, "#ff7090"),
            ("GREEN", g_terr, "#60ff80"),
        ]
        stats.sort(key=lambda s: -s[1])
        leader, lead_terr, lead_color = stats[0]
        second_terr = stats[1][1]

        diff = lead_terr - second_terr
        if diff < 150:
            self.verdict.config(
                text="⚔  THREE-WAY BATTLE  ⚔", fg="#c0b070"
            )
        elif diff < 600:
            self.verdict.config(
                text=f"🏆 {leader} leading (+{diff})", fg=lead_color
            )
        else:
            self.verdict.config(
                text=f"👑 {leader} DOMINATING (+{diff})", fg=lead_color
            )

        self.controls.config(
            text="[Click] BLUE  [Middle] GREEN  [Right] RED   "
                 "[Space] pause  [N] step  [A] auto-war  [R] reset  "
                 "[Up/Down] speed  [Esc] quit"
        )

    def loop(self):
        if not self.game.paused:
            self.game.step()
            self.draw()
        self.root.after(self.delay, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
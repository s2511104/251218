import streamlit as st
import random
import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------
# 1. 설정 및 UI 구성 (Pygame 대체)
# ----------------------------------------------------
st.set_page_config(page_title="Kruskal Braid Maze", layout="centered")

st.title("Kruskal Braid Maze Generator")
st.caption("Pygame Logic ported to Streamlit with Matplotlib")

# 사이드바에서 파라미터 조절
with st.sidebar:
    st.header("설정")
    GRID = st.slider("미로 크기 (GRID)", 5, 50, 25)
    LOOP_PROB = st.slider("루프 생성 확률 (Braid)", 0.0, 1.0, 0.4)
    btn_generate = st.button("미로 생성 (Generate)")

# ----------------------------------------------------
# 2. 미로 생성 로직 (기존 로직 유지)
# ----------------------------------------------------
def generate_maze(grid_size, loop_prob):
    # 초기화
    parent = {}
    rank = {}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a, b):
        ra = find(a)
        rb = find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        else:
            parent[rb] = ra
            if rank[ra] == rank[rb]:
                rank[ra] += 1
        return True

    for r in range(grid_size):
        for c in range(grid_size):
            parent[(r, c)] = (r, c)
            rank[(r, c)] = 0

    walls = []
    for r in range(grid_size):
        for c in range(grid_size):
            if r + 1 < grid_size:
                walls.append(((r, c), (r + 1, c)))
            if c + 1 < grid_size:
                walls.append(((r, c), (r, c + 1)))

    random.shuffle(walls)

    vertical = [[True] * (grid_size - 1) for _ in range(grid_size)]
    horizontal = [[True] * grid_size for _ in range(grid_size - 1)]

    # Kruskal 벽 제거
    for a, b in walls:
        if union(a, b):
            r1, c1 = a
            r2, c2 = b
            if r1 == r2:  # 세로 벽
                vertical[r1][min(c1, c2)] = False
            else:         # 가로 벽
                horizontal[min(r1, r2)][c1] = False

    # Dead-end 제거 (Braid)
    def count_open(r, c):
        cnt = 0
        if r > 0 and not horizontal[r - 1][c]: cnt += 1
        if r < grid_size - 1 and not horizontal[r][c]: cnt += 1
        if c > 0 and not vertical[r][c - 1]: cnt += 1
        if c < grid_size - 1 and not vertical[r][c]: cnt += 1
        return cnt

    for r in range(grid_size):
        for c in range(grid_size):
            if count_open(r, c) == 1:
                if random.random() < loop_prob:
                    dirs = []
                    if r > 0: dirs.append(("U", r - 1, c))
                    if r < grid_size - 1: dirs.append(("D", r + 1, c))
                    if c > 0: dirs.append(("L", r, c - 1))
                    if c < grid_size - 1: dirs.append(("R", r, c + 1))

                    if dirs:
                        d, nr, nc = random.choice(dirs)
                        if d == "U": horizontal[r - 1][c] = False
                        elif d == "D": horizontal[r][c] = False
                        elif d == "L": vertical[r][c - 1] = False
                        elif d == "R": vertical[r][c] = False

    # 타일 맵 생성 (1=벽, 0=통로)
    maze_map = [[1] * (grid_size * 2 + 1) for _ in range(grid_size * 2 + 1)]

    for r in range(grid_size):
        for c in range(grid_size):
            maze_map[r*2+1][c*2+1] = 0

    for r in range(grid_size):
        for c in range(grid_size - 1):
            if not vertical[r][c]:
                maze_map[r*2+1][c*2+2] = 0

    for r in range(grid_size - 1):
        for c in range(grid_size):
            if not horizontal[r][c]:
                maze_map[r*2+2][c*2+1] = 0
    
    return maze_map

# ----------------------------------------------------
# 3. 그리기 및 실행 (Matplotlib 사용)
# ----------------------------------------------------

# 세션 상태를 사용하여 불필요한 재생성 방지
if 'maze' not in st.session_state or btn_generate:
    st.session_state.maze = generate_maze(GRID, LOOP_PROB)

# 시각화
maze_data = np.array(st.session_state.maze)

fig, ax = plt.subplots(figsize=(10, 10))
# cmap: 'binary'는 0을 흰색, 1을 검은색으로 표시 (일반적으로)
# 하지만 imshow 기본값에 따라 다를 수 있으므로 명시적으로 지정
# 여기서는 1(벽)을 검정, 0(길)을 흰색으로 표현하기 위해 'gray' 사용 (0=black, 1=white)
# 로직상 1=벽, 0=길이므로 'gray_r' (reverse)를 쓰거나 데이터를 반전해야 함.
# 가장 확실한 방법: 사용자 지정 컬러맵 혹은 데이터 반전.
# 데이터 반전: 1(벽) -> 0(검정), 0(길) -> 1(흰색)
display_data = 1 - maze_data 

ax.imshow(display_data, cmap='gray', interpolation='nearest')
ax.axis('off')  # 축 숨기기

st.pyplot(fig)

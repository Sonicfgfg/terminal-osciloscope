import numpy as np
import pyaudio
import shutil
import time
import sys
import select
import tty
import termios

# Настройки плавности
FPS = 50             
CHUNK = 1024         
SMOOTHING = 0.4      
COLOR_LINE = "\033[38;5;82m" 
COLOR_RESET = "\033[0m"

# Хранилище для инерции
prev_x = None
prev_y = None

# Текущий режим: 0 = XY (Клубок), 1 = Одна волна, 2 = Две волны
current_mode = 0
mode_names = {0: "XY MODE (LISSAJOUS)", 1: "SINGLE CHANNEL WAVE", 2: "DUAL CHANNEL WAVE"}

def get_braille_char(dots):
    code = 0x2800
    if dots[0][0]: code |= 0x01
    if dots[1][0]: code |= 0x02
    if dots[2][0]: code |= 0x04
    if dots[0][1]: code |= 0x08
    if dots[1][1]: code |= 0x10
    if dots[2][1]: code |= 0x20
    if dots[3][0]: code |= 0x40
    if dots[3][1]: code |= 0x80
    return chr(code)

def draw_line(v_buffer, x0, y0, x1, y1, h, w, thick=False):
    """ Алгоритм Брезенхема с опцией отрисовки жирных линий """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < w and 0 <= y0 < h:
            v_buffer[y0, x0] = True
            if thick:  # Если режим жирный, дорисовываем соседей крестиком
                if x0 + 1 < w: v_buffer[y0, x0 + 1] = True
                if x0 - 1 >= 0: v_buffer[y0, x0 - 1] = True
                if y0 + 1 < h: v_buffer[y0 + 1, x0] = True
                if y0 - 1 >= 0: v_buffer[y0 - 1, x0] = True
                
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def check_keyboard():
    """Проверяет нажатие клавиш без остановки программы"""
    global current_mode
    if select.select([sys.stdin], [], [], 0.0)[0]:
        char = sys.stdin.read(1)
        if char in ('\r', '\n', 'm', 'M'):
            current_mode = (current_mode + 1) % 3

def process_and_draw(data_bytes, width, height):
    global prev_x, prev_y, current_mode
    
    samples = np.frombuffer(data_bytes, dtype=np.int16)
    if len(samples) < 4: return

    # Разделяем каналы
    left_raw = samples[0::2] / 32768.0
    right_raw = samples[1::2] / 32768.0

    # Сглаживание
    if prev_x is not None and len(prev_x) == len(left_raw):
        left = left_raw * (1 - SMOOTHING) + prev_x * SMOOTHING
        right = right_raw * (1 - SMOOTHING) + prev_y * SMOOTHING
    else:
        left, right = left_raw, right_raw

    prev_x, prev_y = left, right

    v_w, v_h = width * 2, height * 4
    v_buffer = np.zeros((v_h, v_w), dtype=bool)
    
    points = []

    # === РЕЖИМ 0: XY ФИГУРЫ (Текущий клубок - ТОНКИЙ) ===
    if current_mode == 0:
        cx, cy = v_w // 2, v_h // 2
        scale_x, scale_y = cx * 0.85, cy * 0.85
        min_len = min(len(left), len(right))
        for i in range(min_len):
            px = int(cx + left[i] * scale_x)
            py = int(cy - right[i] * scale_y)
            points.append((px, py))
            
        for i in range(len(points) - 1):
            draw_line(v_buffer, points[i][0], points[i][1], points[i+1][0], points[i+1][1], v_h, v_w, thick=False)
        if len(points) > 1:
            draw_line(v_buffer, points[-1][0], points[-1][1], points[0][0], points[0][1], v_h, v_w, thick=False)

    # === РЕЖИМ 1: ОДНА ПОЛОСА (Осциллограмма - ЖИРНАЯ) ===
    elif current_mode == 1:
        cy = v_h // 2
        scale_y = cy * 0.8
        num_points = min(len(left), v_w)
        
        for i in range(num_points):
            px = int((i / num_points) * v_w)
            mono_sample = (left[i] + right[i]) / 2.0
            py = int(cy - mono_sample * scale_y)
            points.append((px, py))
            
        for i in range(len(points) - 1):
            draw_line(v_buffer, points[i][0], points[i][1], points[i+1][0], points[i+1][1], v_h, v_w, thick=True)

    # === РЕЖИМ 2: ДВЕ ПОЛОСЫ (Двухканальный режим - ЖИРНЫЕ) ===
    elif current_mode == 2:
        cy_top = v_h // 4
        cy_bottom = (3 * v_h) // 4
        scale_y = (v_h // 4) * 0.8
        
        num_points = min(len(left), v_w)
        
        # Левый канал (сверху)
        points_l = []
        for i in range(num_points):
            px = int((i / num_points) * v_w)
            py = int(cy_top - left[i] * scale_y)
            points_l.append((px, py))
        for i in range(len(points_l) - 1):
            draw_line(v_buffer, points_l[i][0], points_l[i][1], points_l[i+1][0], points_l[i+1][1], v_h, v_w, thick=True)
            
        # Правый канал (снизу)
        points_r = []
        for i in range(num_points):
            px = int((i / num_points) * v_w)
            py = int(cy_bottom - right[i] * scale_y)
            points_r.append((px, py))
        for i in range(len(points_r) - 1):
            draw_line(v_buffer, points_r[i][0], points_r[i][1], points_r[i+1][0], points_r[i+1][1], v_h, v_w, thick=True)

    # Рендеринг буфера в терминал
    output = "\033[H"
    output += f"\033[K MODE: {mode_names[current_mode]} (Press Ctrl+M to switch)\n"
    
    for row in range(0, v_h, 4):
        line_chars = []
        for col in range(0, v_w, 2):
            block = v_buffer[row:row+4, col:col+2]
            if np.any(block):
                line_chars.append(get_braille_char(block))
            else:
                line_chars.append(" ")
        output += "".join(line_chars) + "\n"
    
    sys.stdout.write(COLOR_LINE + output + COLOR_RESET)
    sys.stdout.flush()

def main():
    p = pyaudio.PyAudio()
    try:
        device_index = p.get_default_input_device_info()['index']
    except IOError:
        print("Аудиоустройства не найдены.")
        return

    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    sys.stdout.write("\033[2J\033[?25l")
    sys.stdout.flush()
    
    stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100,
                    input=True, input_device_index=device_index, frames_per_buffer=CHUNK)

    try:
        while True:
            t0 = time.time()
            w, h = shutil.get_terminal_size()
            h -= 4 
            
            check_keyboard()
            
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                process_and_draw(data, w, h)
            except IOError:
                pass
            
            dt = time.time() - t0
            if dt < (1.0 / FPS):
                time.sleep((1.0 / FPS) - dt)
                
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        sys.stdout.write("\033[2J\033[?25h\033[H")
        sys.stdout.flush()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Осциллограф остановлен.")

if __name__ == "__main__":
    main()

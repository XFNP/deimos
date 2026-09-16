import rawscreen

WIDTH = 32
HEIGHT = 16
WIDTH_B = WIDTH // 8

# Simulated display memory
display = bytearray(WIDTH_B * (HEIGHT + 1))

writes = []


def write(address, value):
    writes.append((address, value))

    if 0 <= address < len(display):
        display[address] = value


print("=== rawscreen hardware-independent test ===")
print()

# Make a simple checker/stripe pattern
screen = bytearray(WIDTH_B * HEIGHT)

for y in range(HEIGHT):
    for xb in range(WIDTH_B):
        # Alternating pattern
        if ((y // 2) + xb) & 1:
            screen[y * WIDTH_B + xb] = 0xFF
        else:
            screen[y * WIDTH_B + xb] = 0x00

print("Screen buffer:")
for y in range(HEIGHT):
    row = ""

    for xb in range(WIDTH_B):
        value = screen[y * WIDTH_B + xb]

        for bit in range(8):
            row += "#" if (value & (0x80 >> bit)) else "."

    print(row)

print()

print("Calling rawscreen.apply()...")

rawscreen.apply(
    write,
    0,              # const_select
    0,              # const_buffer
    WIDTH_B,        # const_width_b
    WIDTH_B,        # const_true_width_b
    HEIGHT,         # const_height
    0,              # const_header
    screen,
    None,           # oldbuffer
    0,              # plane
    0,
    0,
    WIDTH_B - 1,
    HEIGHT - 1
)

print("Number of writes:", len(writes))
print()

print("First writes:")
for address, value in writes[:20]:
    print(f"address={address:4d} value=0x{value:02X}")

print()

print("Simulated display memory:")

for y in range(HEIGHT + 1):
    row = ""

    for xb in range(WIDTH_B):
        value = display[y * WIDTH_B + xb]

        for bit in range(8):
            row += "#" if (value & (0x80 >> bit)) else "."

    print(row)

print()
print("=== image() test ===")

paint_calls = []


def paint(x, y, plane, brush, value):
    paint_calls.append((x, y, plane, brush, value))


image = bytearray([
    0xFF,
    0x00,
    0x81,
    0x00,
    0xBD,
    0x00,
    0xFF,
    0x00,
])

rawscreen.image(
    0,              # x
    0,              # y
    16,             # image width
    4,              # image height
    0xFF,           # v
    0x01,           # const_bright
    0x02,           # const_dark
    32,              # const_width
    16,             # const_height
    paint,
    image
)

print("Paint calls:", len(paint_calls))

for call in paint_calls[:20]:
    x, y, plane, brush, value = call
    print(
        f"x={x:3d} "
        f"y={y:3d} "
        f"plane={plane} "
        f"brush=0x{brush:06X} "
        f"value={value}"
    )

print()
print("=== done ===")

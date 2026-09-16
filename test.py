import rawscreen


print("=== rawscreen test ===")
print("module:", rawscreen)
print()


# ------------------------------------------------------------
# 1. Check functions
# ------------------------------------------------------------

print("Functions:")

for name in (
    "in_bounds",
    "clear",
    "apply",
    "image",
):
    print(
        " ",
        name,
        "OK" if hasattr(rawscreen, name) else "MISSING"
    )

print()


# ------------------------------------------------------------
# 2. Test in_bounds()
# ------------------------------------------------------------

print("=== in_bounds ===")

tests = [
    (0, 0, 10, 10),
    (9, 9, 10, 10),
    (10, 10, 10, 10),
    (-1, 0, 10, 10),
    (0, -1, 10, 10),
]

for x, y, w, h in tests:
    print(
        f"in_bounds({x}, {y}, {w}, {h}) =",
        rawscreen.in_bounds(x, y, w, h)
    )

print()


# ------------------------------------------------------------
# 3. Test clear()
# ------------------------------------------------------------

print("=== clear ===")

buffer = bytearray([
    0x11,
    0x22,
    0x33,
    0x44,
    0x55,
    0x66,
    0x77,
    0x88,
])

print("before:", buffer.hex())

rawscreen.clear(
    buffer,
    2,
    6
)

print("after: ", buffer.hex())

print()


# ------------------------------------------------------------
# 4. Test apply()
# ------------------------------------------------------------

print("=== apply ===")

writes = []


def write(address, data):
    print(
        f"WRITE address={address} data={data}"
    )

    writes.append(
        (address, data)
    )


# A small fake screen buffer.
#
# width = 8 bytes
# height = 4 rows
#
# Put obvious non-zero data into it.

screen = bytearray([
    0x01, 0x02, 0x03, 0x04,
    0x05, 0x06, 0x07, 0x08,

    0x11, 0x12, 0x13, 0x14,
    0x15, 0x16, 0x17, 0x18,

    0x21, 0x22, 0x23, 0x24,
    0x25, 0x26, 0x27, 0x28,

    0x31, 0x32, 0x33, 0x34,
    0x35, 0x36, 0x37, 0x38,
])


# No old buffer means every pixel
# should be considered changed.

oldscreen = None


rawscreen.apply(
    write,

    # const_select
    100,

    # const_buffer
    200,

    # const_width_b
    8,

    # const_true_width_b
    8,

    # const_height
    4,

    # const_header
    0,

    # buffer
    screen,

    # oldbuffer
    oldscreen,

    # plane
    0,

    # start_x
    0,

    # start_y
    0,

    # end_x
    7,

    # end_y
    3,
)


print()
print("Total writes:", len(writes))

print()


# ------------------------------------------------------------
# 5. Test apply() with old buffer
# ------------------------------------------------------------

print("=== apply() changed-pixel test ===")

writes.clear()


oldscreen = bytearray(screen)

# Change exactly one byte.
screen[10] = 0xFE


rawscreen.apply(
    write,

    100,
    200,
    8,
    8,
    4,
    0,

    screen,
    oldscreen,

    1,

    0,
    0,
    7,
    3,
)


print()
print(
    "Changed-pixel writes:",
    len(writes)
)

print()


# ------------------------------------------------------------
# 6. Test image()
# ------------------------------------------------------------

print("=== image ===")

paint_calls = []


def paint(
    x,
    y,
    plane,
    brush,
    value
):
    print(
        "PAINT",
        "x=", x,
        "y=", y,
        "plane=", plane,
        "brush=", hex(brush),
        "value=", value
    )

    paint_calls.append(
        (
            x,
            y,
            plane,
            brush,
            value
        )
    )


# 16x4 monochrome image.
#
# 2 bytes per row.

image = bytearray([
    0xFF, 0x00,
    0x81, 0x00,
    0xBD, 0x00,
    0xFF, 0x00,
])


rawscreen.image(
    # x
    0,

    # y
    0,

    # w
    16,

    # h
    4,

    # v
    0xFF,

    # const_bright
    0x01,

    # const_dark
    0x02,

    # const_width
    16,

    # const_height
    4,

    # paint
    paint,

    # image
    image,
)


print()
print(
    "Total paint calls:",
    len(paint_calls)
)

print()


# ------------------------------------------------------------
# Final result
# ------------------------------------------------------------

print("=== result ===")

if not hasattr(rawscreen, "apply"):
    print("FAIL: rawscreen.apply() missing")
elif len(writes) == 0:
    print("WARNING: apply() produced no writes")
else:
    print("apply() produced writes")

if len(paint_calls) == 0:
    print("WARNING: image() produced no paint calls")
else:
    print("image() produced paint calls")

print()
print("=== done ===")

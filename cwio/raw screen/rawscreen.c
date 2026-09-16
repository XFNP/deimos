#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdint.h>
#include <stdbool.h>

/*
 * Equivalent of:
 *
 * static mp_int_t in_bounds_raw(...)
 */
static int in_bounds_raw(
    int x,
    int y,
    int w,
    int h
) {
    return x >= 0 &&
           x < w &&
           y >= 0 &&
           y < h;
}


/*
 * Python:
 *
 * rawscreen.in_bounds(x, y, w, h)
 */
static PyObject *rawscreen_in_bounds(
    PyObject *self,
    PyObject *args
) {
    int x;
    int y;
    int w;
    int h;

    if (!PyArg_ParseTuple(
            args,
            "iiii",
            &x,
            &y,
            &w,
            &h)) {
        return NULL;
    }

    if (in_bounds_raw(x, y, w, h))
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}


/*
 * Python:
 *
 * rawscreen.clear(buffer, start, end)
 *
 * Equivalent to the MicroPython implementation.
 */
static PyObject *rawscreen_clear(
    PyObject *self,
    PyObject *args
) {
    PyObject *buffer_obj;
    int start;
    int end;

    if (!PyArg_ParseTuple(
            args,
            "Oii",
            &buffer_obj,
            &start,
            &end)) {
        return NULL;
    }

    Py_buffer buffer;

    if (PyObject_GetBuffer(
            buffer_obj,
            &buffer,
            PyBUF_WRITABLE) < 0) {
        return NULL;
    }

    uint8_t *data =
        (uint8_t *)buffer.buf;

    if (start < 0)
        start = 0;

    if (end > buffer.len)
        end = (int)buffer.len;

    for (int i = start; i < end; i++)
        data[i] = 0x00;

    PyBuffer_Release(&buffer);

    Py_RETURN_NONE;
}


/*
 * Equivalent to the original:
 *
 * WRITE(addr, data)
 */
static int call_write(
    PyObject *write,
    int addr,
    int data
) {
    PyObject *result =
        PyObject_CallFunction(
            write,
            "ii",
            addr,
            data
        );

    if (result == NULL)
        return -1;

    Py_DECREF(result);

    return 0;
}


/*
 * Equivalent to:
 *
 * PAINT(x, y, plane, brush, v)
 */
static int call_paint(
    PyObject *paint,
    int x,
    int y,
    int plane,
    int brush,
    int value
) {
    PyObject *result =
        PyObject_CallFunction(
            paint,
            "iiiii",
            x,
            y,
            plane,
            brush,
            value
        );

    if (result == NULL)
        return -1;

    Py_DECREF(result);

    return 0;
}


/*
 * Python:
 *
 * rawscreen.apply(
 *     write,
 *     const_select,
 *     const_buffer,
 *     const_width_b,
 *     const_true_width_b,
 *     const_height,
 *     const_header,
 *     buffer,
 *     oldbuffer,
 *     plane,
 *     start_x,
 *     start_y,
 *     end_x,
 *     end_y
 * )
 */
static PyObject *rawscreen_apply(
    PyObject *self,
    PyObject *args
) {
    PyObject *write;
    int const_select;
    int const_buffer;
    int const_width_b;
    int const_true_width_b;
    int const_height;
    int const_header;
    PyObject *buffer;
    PyObject *oldbuffer;
    int plane;
    int start_x;
    int start_y;
    int end_x;
    int end_y;

    if (!PyArg_ParseTuple(
            args,
            "OiiiiiiOOiiiii",
            &write,
            &const_select,
            &const_buffer,
            &const_width_b,
            &const_true_width_b,
            &const_height,
            &const_header,
            &buffer,
            &oldbuffer,
            &plane,
            &start_x,
            &start_y,
            &end_x,
            &end_y)) {
        return NULL;
    }

    Py_buffer bufinfo;
    Py_buffer oldbufinfo;

    if (PyObject_GetBuffer(
            buffer,
            &bufinfo,
            PyBUF_WRITABLE) < 0) {
        return NULL;
    }

    uint8_t *buf =
        (uint8_t *)bufinfo.buf;

    bool oldbuf_none =
        oldbuffer == Py_None;

    uint8_t *oldbuf = NULL;

    if (!oldbuf_none) {
        if (PyObject_GetBuffer(
                oldbuffer,
                &oldbufinfo,
                PyBUF_SIMPLE) < 0) {
            PyBuffer_Release(&bufinfo);
            return NULL;
        }

        oldbuf =
            (uint8_t *)oldbufinfo.buf;
    }

    /*
     * WRITE(const_select, plane)
     */
    if (call_write(
            write,
            const_select,
            plane) < 0) {

        if (!oldbuf_none)
            PyBuffer_Release(&oldbufinfo);

        PyBuffer_Release(&bufinfo);

        return NULL;
    }

    /*
     * Header.
     */
    for (int y = 0;
         y < const_header;
         y++) {

        for (int x = 0;
             x < const_width_b;
             x++) {

            int i =
                (const_height + y) *
                const_width_b +
                x;

            if (
                oldbuf_none ||
                oldbuf[i] != buf[i]
            ) {
                if (call_write(
                        write,
                        const_buffer +
                            y * const_true_width_b +
                            x,
                        buf[i]) < 0) {

                    if (!oldbuf_none)
                        PyBuffer_Release(&oldbufinfo);

                    PyBuffer_Release(&bufinfo);

                    return NULL;
                }
            }
        }
    }

    /*
     * Changed image region.
     */
    for (int y = start_y;
         y <= end_y;
         y++) {

        for (int x = start_x;
             x <= end_x;
             x++) {

            int i =
                y * const_width_b +
                x;

            if (
                oldbuf_none ||
                oldbuf[i] != buf[i]
            ) {
                if (call_write(
                        write,
                        const_buffer +
                            (y + 1) *
                            const_true_width_b +
                            x,
                        buf[i]) < 0) {

                    if (!oldbuf_none)
                        PyBuffer_Release(&oldbufinfo);

                    PyBuffer_Release(&bufinfo);

                    return NULL;
                }
            }
        }
    }

    if (!oldbuf_none)
        PyBuffer_Release(&oldbufinfo);

    PyBuffer_Release(&bufinfo);

    Py_RETURN_NONE;
}


/*
 * Python:
 *
 * rawscreen.image(
 *     x, y, w, h, v,
 *     const_bright,
 *     const_dark,
 *     const_width,
 *     const_height,
 *     paint,
 *     image
 * )
 */
static PyObject *rawscreen_image(
    PyObject *self,
    PyObject *args
) {
    int x;
    int y;
    int w;
    int h;
    int v;
    int const_bright;
    int const_dark;
    int const_width;
    int const_height;

    PyObject *paint;
    PyObject *image;

    if (!PyArg_ParseTuple(
            args,
            "iiiiiiiiiOO",
            &x,
            &y,
            &w,
            &h,
            &v,
            &const_bright,
            &const_dark,
            &const_width,
            &const_height,
            &paint,
            &image)) {
        return NULL;
    }

    Py_buffer imageinfo;

    if (PyObject_GetBuffer(
            image,
            &imageinfo,
            PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    uint8_t *img =
        (uint8_t *)imageinfo.buf;

    bool draw = false;

    /*
     * Actual row size in bytes.
     *
     * ((w + 7) & ~7) / 8
     */
    int wb =
        ((w + 7) & ~7) / 8;

    for (int py = 0;
         py < h;
         py++) {

        if (!draw) {
            draw =
                in_bounds_raw(
                    0,
                    y + py,
                    const_width,
                    const_height
                );
        }

        if (draw) {

            if (!in_bounds_raw(
                    0,
                    y + py,
                    const_width,
                    const_height)) {

                PyBuffer_Release(&imageinfo);
                Py_RETURN_NONE;
            }

            for (int bx = 0;
                 bx < wb;
                 bx++) {

                int ox =
                    x % 8;

                /*
                 * Handle negative x correctly.
                 */
                if (ox < 0)
                    ox += 8;

                int r =
                    py * wb + bx;

                int prevb =
                    (bx == 0)
                    ? 0x00
                    : img[r - 1];

                int currb =
                    img[r];

                int nextb =
                    (bx == wb - 1)
                    ? 0x00
                    : img[r + 1];

                /*
                 * Three adjacent bytes merged together.
                 */
                uint32_t brush =
                    ((uint32_t)prevb << 16) |
                    ((uint32_t)currb << 8) |
                    nextb;

                /*
                 * First shifted byte.
                 */
                int byte =
                    (int)(brush >> (8 + ox));

                if (byte) {

                    if (call_paint(
                            paint,
                            x + bx * 8,
                            y + py,
                            0,
                            byte,
                            v & const_bright) < 0) {

                        PyBuffer_Release(&imageinfo);
                        return NULL;
                    }

                    if (call_paint(
                            paint,
                            x + bx * 8,
                            y + py,
                            1,
                            byte,
                            v & const_dark) < 0) {

                        PyBuffer_Release(&imageinfo);
                        return NULL;
                    }
                }

                /*
                 * Remaining part crossing the byte
                 * boundary.
                 */
                byte =
                    (int)(brush >> ox);

                if (byte) {

                    if (call_paint(
                            paint,
                            x + (bx + 1) * 8,
                            y + py,
                            0,
                            byte,
                            v & const_bright) < 0) {

                        PyBuffer_Release(&imageinfo);
                        return NULL;
                    }

                    if (call_paint(
                            paint,
                            x + (bx + 1) * 8,
                            y + py,
                            1,
                            byte,
                            v & const_dark) < 0) {

                        PyBuffer_Release(&imageinfo);
                        return NULL;
                    }
                }
            }
        }
    }

    PyBuffer_Release(&imageinfo);

    Py_RETURN_NONE;
}


/* ------------------------------------------------------------ */
/* Module definition                                             */
/* ------------------------------------------------------------ */

static PyMethodDef rawscreen_methods[] = {

    {
        "in_bounds",
        rawscreen_in_bounds,
        METH_VARARGS,
        "Check whether a coordinate is inside a rectangle."
    },

    {
        "clear",
        rawscreen_clear,
        METH_VARARGS,
        "Clear a range of a screen buffer."
    },

    {
        "apply",
        rawscreen_apply,
        METH_VARARGS,
        "Apply changed screen-buffer data."
    },

    {
        "image",
        rawscreen_image,
        METH_VARARGS,
        "Draw a 1-bit image into the display."
    },

    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef rawscreen_module = {
    PyModuleDef_HEAD_INIT,
    "rawscreen",
    "Deimos raw-screen routines.",
    -1,
    rawscreen_methods
};


PyMODINIT_FUNC PyInit_rawscreen(void)
{
    return PyModule_Create(
        &rawscreen_module
    );
}

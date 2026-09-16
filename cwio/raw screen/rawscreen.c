#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>


/*
 * rawscreen CPython port
 *
 * Original MicroPython API:
 *
 *   in_bounds(x, y, w, h)
 *   clear(buffer, start, end)
 *   apply(write, const_select, const_buffer,
 *         const_width_b, const_true_width_b,
 *         const_height, const_header,
 *         buffer, oldbuffer, plane,
 *         start_x, start_y, end_x, end_y)
 *
 *   image(x, y, w, h, v,
 *         const_bright, const_dark,
 *         const_width, const_height,
 *         paint, image)
 */


static int debug_write_count = 0;


/* --------------------------------------------------------- */
/* Helpers                                                   */
/* --------------------------------------------------------- */

static int in_bounds_raw(
    int x,
    int y,
    int w,
    int h
) {
    return x >= 0 && x < w && y >= 0 && y < h;
}


/*
 * Call:
 *
 *     write(address, data)
 */
static int call_write(
    PyObject *write,
    int address,
    int data
) {
    PyObject *args;
    PyObject *result;

    args = Py_BuildValue(
        "(ii)",
        address,
        data
    );

    if (!args) {
        return -1;
    }

    if (debug_write_count < 20) {
        printf(
            "rawscreen: WRITE addr=%d data=%d\n",
            address,
            data
        );
        fflush(stdout);

        debug_write_count++;
    }

    result = PyObject_CallObject(write, args);

    Py_DECREF(args);

    if (!result) {
        return -1;
    }

    Py_DECREF(result);

    return 0;
}


/*
 * Call:
 *
 *     paint(x, y, plane, brush, value)
 */
static int call_paint(
    PyObject *paint,
    int x,
    int y,
    int plane,
    int brush,
    int value
) {
    PyObject *args;
    PyObject *result;

    args = Py_BuildValue(
        "(iiiii)",
        x,
        y,
        plane,
        brush,
        value
    );

    if (!args) {
        return -1;
    }

    result = PyObject_CallObject(paint, args);

    Py_DECREF(args);

    if (!result) {
        return -1;
    }

    Py_DECREF(result);

    return 0;
}


/* --------------------------------------------------------- */
/* in_bounds                                                 */
/* --------------------------------------------------------- */

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
        &h
    )) {
        return NULL;
    }

    return PyBool_FromLong(
        in_bounds_raw(x, y, w, h)
    );
}


/* --------------------------------------------------------- */
/* clear                                                      */
/* --------------------------------------------------------- */

static PyObject *rawscreen_clear(
    PyObject *self,
    PyObject *args
) {
    PyObject *buffer;
    int start;
    int end;

    Py_buffer buf;

    if (!PyArg_ParseTuple(
        args,
        "Oii",
        &buffer,
        &start,
        &end
    )) {
        return NULL;
    }

    if (PyObject_GetBuffer(
        buffer,
        &buf,
        PyBUF_WRITABLE
    ) < 0) {
        return NULL;
    }

    uint8_t *data = (uint8_t *)buf.buf;

    if (start < 0)
        start = 0;

    if (end > (int)buf.len)
        end = (int)buf.len;

    for (int i = start; i < end; i++) {
        data[i] = 0x00;
    }

    PyBuffer_Release(&buf);

    Py_RETURN_NONE;
}


/* --------------------------------------------------------- */
/* apply                                                       */
/* --------------------------------------------------------- */

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

    Py_buffer bufinfo;
    Py_buffer oldbufinfo;

    bool oldbuf_none;

    uint8_t *buf = NULL;
    uint8_t *oldbuf = NULL;


    printf("rawscreen.apply() called\n");
    fflush(stdout);


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
        &end_y
    )) {
        return NULL;
    }


    printf(
        "rawscreen.apply: "
        "select=%d buffer=%d width_b=%d true_width_b=%d "
        "height=%d header=%d plane=%d "
        "region=(%d,%d)-(%d,%d)\n",
        const_select,
        const_buffer,
        const_width_b,
        const_true_width_b,
        const_height,
        const_header,
        plane,
        start_x,
        start_y,
        end_x,
        end_y
    );

    fflush(stdout);


    if (!PyCallable_Check(write)) {
        PyErr_SetString(
            PyExc_TypeError,
            "write must be callable"
        );
        return NULL;
    }


    if (PyObject_GetBuffer(
        buffer,
        &bufinfo,
        PyBUF_WRITABLE
    ) < 0) {
        return NULL;
    }

    buf = (uint8_t *)bufinfo.buf;


    oldbuf_none = oldbuffer == Py_None;

    if (!oldbuf_none) {
        if (PyObject_GetBuffer(
            oldbuffer,
            &oldbufinfo,
            PyBUF_SIMPLE
        ) < 0) {
            PyBuffer_Release(&bufinfo);
            return NULL;
        }

        oldbuf = (uint8_t *)oldbufinfo.buf;
    }


    /*
     * Select display plane.
     */

    printf(
        "rawscreen.apply: selecting plane %d\n",
        plane
    );

    fflush(stdout);


    if (call_write(
        write,
        const_select,
        plane
    ) < 0) {
        goto error;
    }


    /*
     * Header.
     */

    printf(
        "rawscreen.apply: processing header (%d rows)\n",
        const_header
    );

    fflush(stdout);


    for (int y = 0; y < const_header; y++) {

        for (int x = 0; x < const_width_b; x++) {

            int i =
                (const_height + y)
                * const_width_b
                + x;


            bool changed =
                oldbuf_none ||
                oldbuf[i] != buf[i];


            if (changed) {

                if (debug_write_count < 20) {
                    printf(
                        "rawscreen.apply: "
                        "header pixel i=%d value=%u\n",
                        i,
                        buf[i]
                    );

                    fflush(stdout);
                }


                if (call_write(
                    write,
                    const_buffer
                        + y * const_true_width_b
                        + x,
                    buf[i]
                ) < 0) {
                    goto error;
                }
            }
        }
    }


    /*
     * Main screen area.
     */

    printf(
        "rawscreen.apply: processing region\n"
    );

    fflush(stdout);


    for (int y = start_y; y <= end_y; y++) {

        for (int x = start_x; x <= end_x; x++) {

            int i =
                y * const_width_b
                + x;


            bool changed =
                oldbuf_none ||
                oldbuf[i] != buf[i];


            if (changed) {

                if (debug_write_count < 20) {
                    printf(
                        "rawscreen.apply: "
                        "screen pixel x=%d y=%d i=%d value=%u\n",
                        x,
                        y,
                        i,
                        buf[i]
                    );

                    fflush(stdout);
                }


                if (call_write(
                    write,
                    const_buffer
                        + (y + 1)
                        * const_true_width_b
                        + x,
                    buf[i]
                ) < 0) {
                    goto error;
                }
            }
        }
    }


    printf(
        "rawscreen.apply: finished\n"
    );

    fflush(stdout);


    PyBuffer_Release(&bufinfo);

    if (!oldbuf_none) {
        PyBuffer_Release(&oldbufinfo);
    }

    Py_RETURN_NONE;


error:

    PyBuffer_Release(&bufinfo);

    if (!oldbuf_none) {
        PyBuffer_Release(&oldbufinfo);
    }

    return NULL;
}


/* --------------------------------------------------------- */
/* image                                                       */
/* --------------------------------------------------------- */

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

    Py_buffer imageinfo;

    uint8_t *img;

    bool draw = false;


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
        &image
    )) {
        return NULL;
    }


    if (!PyCallable_Check(paint)) {
        PyErr_SetString(
            PyExc_TypeError,
            "paint must be callable"
        );
        return NULL;
    }


    if (PyObject_GetBuffer(
        image,
        &imageinfo,
        PyBUF_SIMPLE
    ) < 0) {
        return NULL;
    }


    img = (uint8_t *)imageinfo.buf;


    /*
     * Actual row size in bytes.
     */

    int wb =
        ((w + 7) & ~7) / 8;


    for (int py = 0; py < h; py++) {

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
                const_height
            )) {
                break;
            }


            for (int bx = 0; bx < wb; bx++) {

                int ox = x % 8;


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


                int brush =
                    (prevb << 16)
                    | (currb << 8)
                    | nextb;


                /*
                 * First byte.
                 */

                int byte =
                    brush >> (8 + ox);


                if (byte) {

                    if (call_paint(
                        paint,
                        x + bx * 8,
                        y + py,
                        0,
                        byte,
                        v & const_bright
                    ) < 0) {
                        PyBuffer_Release(&imageinfo);
                        return NULL;
                    }


                    if (call_paint(
                        paint,
                        x + bx * 8,
                        y + py,
                        1,
                        byte,
                        v & const_dark
                    ) < 0) {
                        PyBuffer_Release(&imageinfo);
                        return NULL;
                    }
                }


                /*
                 * Remaining part crossing
                 * the byte boundary.
                 */

                byte =
                    brush >> ox;


                if (byte) {

                    if (call_paint(
                        paint,
                        x + (bx + 1) * 8,
                        y + py,
                        0,
                        byte,
                        v & const_bright
                    ) < 0) {
                        PyBuffer_Release(&imageinfo);
                        return NULL;
                    }


                    if (call_paint(
                        paint,
                        x + (bx + 1) * 8,
                        y + py,
                        1,
                        byte,
                        v & const_dark
                    ) < 0) {
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


/* --------------------------------------------------------- */
/* Module methods                                             */
/* --------------------------------------------------------- */

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
        "Clear a section of a buffer."
    },

    {
        "apply",
        rawscreen_apply,
        METH_VARARGS,
        "Apply a screen buffer."
    },

    {
        "image",
        rawscreen_image,
        METH_VARARGS,
        "Draw a monochrome image."
    },

    {
        NULL,
        NULL,
        0,
        NULL
    }
};


/* --------------------------------------------------------- */
/* Module definition                                          */
/* --------------------------------------------------------- */

static struct PyModuleDef raw_screen_module = {
    PyModuleDef_HEAD_INIT,
    "rawscreen",
    "Deimos raw screen acceleration module.",
    -1,
    rawscreen_methods
};


PyMODINIT_FUNC PyInit_rawscreen(void) {
    return PyModule_Create(
        &rawscreen_module
    );
}

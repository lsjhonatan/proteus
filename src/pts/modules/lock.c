/*
 * Trestle - Roteador de Anonimato em C para Raspberry Pi
 * Copyright (C) 2026  Jhonatan L. Santos
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <Python.h>
#include <fcntl.h>
#include <unistd.h>

static PyObject* lock_acquire(PyObject *self, PyObject *args) {
    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL;
    }
    
    int fd = open(path, O_CREAT | O_RDWR, 0644);
    if (fd == -1) {
        PyErr_SetString(PyExc_IOError, "Erro ao abrir arquivo de lock");
        return NULL;
    }
    
    if (flock(fd, LOCK_EX) == -1) {
        close(fd);
        PyErr_SetString(PyExc_IOError, "Erro ao adquirir lock");
        return NULL;
    }
    
    return PyLong_FromLong(fd);
}

static PyObject* lock_release(PyObject *self, PyObject *args) {
    int fd;
    if (!PyArg_ParseTuple(args, "i", &fd)) {
        return NULL;
    }
    
    flock(fd, LOCK_UN);
    close(fd);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"acquire", lock_acquire, METH_VARARGS, "Adquire lock"},
    {"release", lock_release, METH_VARARGS, "Libera lock"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_lock",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit__lock(void) {
    return PyModule_Create(&module);
}

#include <Python.h>
#include <fcntl.h>
#include <sys/file.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#define DEFAULT_TIMEOUT 30

static int acquire_lock(const char *path, int timeout) {
    int fd = open(path, O_CREAT | O_RDWR, 0644);
    if (fd == -1) {
        return -1;
    }

    int ret = flock(fd, LOCK_EX | LOCK_NB);
    int tries = 0;

    while (ret == -1 && errno == EWOULDBLOCK && tries < timeout) {
        sleep(1);
        tries++;
        ret = flock(fd, LOCK_EX | LOCK_NB);
    }

    if (ret == -1) {
        close(fd);
        return -1;
    }
    return fd;
}

static void release_lock(int fd) {
    if (fd != -1) {
        flock(fd, LOCK_UN);
        close(fd);
    }
}

static PyObject* lock_acquire(PyObject *self, PyObject *args) {
    const char *path;
    int timeout = DEFAULT_TIMEOUT;
    int fd;

    if (!PyArg_ParseTuple(args, "s|i", &path, &timeout)) {
        return NULL;
    }

    fd = acquire_lock(path, timeout);
    if (fd == -1) {
        PyErr_SetString(PyExc_IOError, "Nao foi possivel adquirir lock");
        return NULL;
    }

    return PyLong_FromLong(fd);
}

static PyObject* lock_release(PyObject *self, PyObject *args) {
    int fd;
    if (!PyArg_ParseTuple(args, "i", &fd)) {
        return NULL;
    }

    release_lock(fd);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"acquire", lock_acquire, METH_VARARGS, "Adquire lock exclusivo"},
    {"release", lock_release, METH_VARARGS, "Libera lock"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_lock",
    "Modulo C para lock de arquivos com flock",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__lock(void) {
    return PyModule_Create(&module);
}

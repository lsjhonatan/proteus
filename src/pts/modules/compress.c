#include <Python.h>
#include <zstd.h>
#include <string.h>
#include <stdlib.h>

static PyObject* compress_zstd(PyObject *self, PyObject *args) {
    const char *data;
    Py_ssize_t data_len;
    size_t max_compressed_size;
    void *compressed;
    size_t compressed_size;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "y#", &data, &data_len)) {
        return NULL;
    }

    max_compressed_size = ZSTD_compressBound(data_len);
    compressed = malloc(max_compressed_size);
    if (!compressed) {
        PyErr_SetString(PyExc_MemoryError, "Falha ao alocar memoria para compressao");
        return NULL;
    }

    compressed_size = ZSTD_compress(compressed, max_compressed_size, data, data_len, 3);
    if (ZSTD_isError(compressed_size)) {
        free(compressed);
        PyErr_SetString(PyExc_RuntimeError, ZSTD_getErrorName(compressed_size));
        return NULL;
    }

    result = PyBytes_FromStringAndSize(compressed, compressed_size);
    free(compressed);
    return result;
}

static PyObject* decompress_zstd(PyObject *self, PyObject *args) {
    const char *compressed;
    Py_ssize_t compressed_size;
    unsigned long long decompressed_size;
    void *decompressed;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "y#", &compressed, &compressed_size)) {
        return NULL;
    }

    decompressed_size = ZSTD_getFrameContentSize(compressed, compressed_size);
    if (decompressed_size == ZSTD_CONTENTSIZE_ERROR) {
        PyErr_SetString(PyExc_RuntimeError, "Dados comprimidos invalidos");
        return NULL;
    }
    if (decompressed_size == ZSTD_CONTENTSIZE_UNKNOWN) {
        PyErr_SetString(PyExc_RuntimeError, "Tamanho original desconhecido");
        return NULL;
    }

    decompressed = malloc(decompressed_size);
    if (!decompressed) {
        PyErr_SetString(PyExc_MemoryError, "Falha ao alocar memoria para descompressao");
        return NULL;
    }

    size_t result_size = ZSTD_decompress(decompressed, decompressed_size, compressed, compressed_size);
    if (ZSTD_isError(result_size)) {
        free(decompressed);
        PyErr_SetString(PyExc_RuntimeError, ZSTD_getErrorName(result_size));
        return NULL;
    }

    result = PyBytes_FromStringAndSize(decompressed, result_size);
    free(decompressed);
    return result;
}

static PyMethodDef methods[] = {
    {"compress", compress_zstd, METH_VARARGS, "Comprime dados com Zstandard"},
    {"decompress", decompress_zstd, METH_VARARGS, "Descomprime dados Zstandard"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_compress",
    "Modulo C para compressao Zstandard",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__compress(void) {
    return PyModule_Create(&module);
}

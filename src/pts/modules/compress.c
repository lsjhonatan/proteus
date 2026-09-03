/*
 * Proteus Tool Suit - Gerenciador de Pacotes Universal.
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
#include <zstd.h>
#include <string.h>
#include <stdlib.h>

/**
 * Módulo de compressão Zstandard para Proteus Tool Suite
 * 
 * Implementa compressão e descompressão usando Zstandard,
 * com interface Python otimizada para snapshots.
 */

static PyObject* compress_zstd(PyObject *self, PyObject *args) {
    const char *data;
    Py_ssize_t data_len;
    size_t max_compressed_size;
    void *compressed;
    size_t compressed_size;
    PyObject *result;
    
    if (!PyArg_ParseTuple(args, "s#", &data, &data_len)) {
        return NULL;
    }
    
    max_compressed_size = ZSTD_compressBound(data_len);
    compressed = malloc(max_compressed_size);
    if (!compressed) {
        PyErr_SetString(PyExc_MemoryError, "Falha ao alocar memória para compressão");
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
    
    if (!PyArg_ParseTuple(args, "s#", &compressed, &compressed_size)) {
        return NULL;
    }
    
    decompressed_size = ZSTD_getFrameContentSize(compressed, compressed_size);
    if (decompressed_size == ZSTD_CONTENTSIZE_ERROR) {
        PyErr_SetString(PyExc_RuntimeError, "Dados comprimidos inválidos");
        return NULL;
    }
    if (decompressed_size == ZSTD_CONTENTSIZE_UNKNOWN) {
        PyErr_SetString(PyExc_RuntimeError, "Tamanho original desconhecido");
        return NULL;
    }
    
    decompressed = malloc(decompressed_size);
    if (!decompressed) {
        PyErr_SetString(PyExc_MemoryError, "Falha ao alocar memória para descompressão");
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
    "Módulo C para compressão Zstandard",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__compress(void) {
    return PyModule_Create(&module);
}

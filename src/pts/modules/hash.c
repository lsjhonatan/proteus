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
#include <openssl/sha.h>

static PyObject* hash_sha256(PyObject *self, PyObject *args) {
    const char *input;
    Py_ssize_t input_len;
    unsigned char hash[SHA256_DIGEST_LENGTH];
    
    if (!PyArg_ParseTuple(args, "s#", &input, &input_len)) {
        return NULL;
    }
    
    SHA256_CTX ctx;
    SHA256_Init(&ctx);
    SHA256_Update(&ctx, input, input_len);
    SHA256_Final(hash, &ctx);
    
    return PyBytes_FromStringAndSize((char*)hash, SHA256_DIGEST_LENGTH);
}

static PyMethodDef methods[] = {
    {"sha256", hash_sha256, METH_VARARGS, "SHA-256 hash"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_hash",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit__hash(void) {
    return PyModule_Create(&module);
}

#include <Python.h>
#include <openssl/evp.h>
#include <string.h>
#include <stdlib.h>

static PyObject* hash_sha256(PyObject *self, PyObject *args) {
    const char *input;
    Py_ssize_t input_len;
    unsigned char hash[32];
    unsigned int hash_len = 32;
    EVP_MD_CTX *ctx;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "s#", &input, &input_len)) {
        return NULL;
    }

    ctx = EVP_MD_CTX_new();
    if (!ctx) {
        PyErr_SetString(PyExc_MemoryError, "Falha ao criar contexto EVP");
        return NULL;
    }

    EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);
    EVP_DigestUpdate(ctx, input, input_len);
    EVP_DigestFinal_ex(ctx, hash, &hash_len);
    EVP_MD_CTX_free(ctx);

    result = PyBytes_FromStringAndSize((char*)hash, hash_len);
    return result;
}

static PyObject* hash_file_sha256(PyObject *self, PyObject *args) {
    const char *filename;
    FILE *file;
    unsigned char buffer[8192];
    size_t bytes_read;
    unsigned char hash[32];
    unsigned int hash_len = 32;
    EVP_MD_CTX *ctx;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "s", &filename)) {
        return NULL;
    }

    file = fopen(filename, "rb");
    if (!file) {
        PyErr_SetString(PyExc_IOError, "Nao foi possivel abrir o arquivo");
        return NULL;
    }

    ctx = EVP_MD_CTX_new();
    if (!ctx) {
        fclose(file);
        PyErr_SetString(PyExc_MemoryError, "Falha ao criar contexto EVP");
        return NULL;
    }

    EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);

    while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        EVP_DigestUpdate(ctx, buffer, bytes_read);
    }

    EVP_DigestFinal_ex(ctx, hash, &hash_len);
    EVP_MD_CTX_free(ctx);
    fclose(file);

    result = PyBytes_FromStringAndSize((char*)hash, hash_len);
    return result;
}

static PyMethodDef methods[] = {
    {"sha256", hash_sha256, METH_VARARGS, "SHA-256 hash de uma string"},
    {"file_sha256", hash_file_sha256, METH_VARARGS, "SHA-256 hash de um arquivo"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_hash",
    "Modulo C para hashing SHA-256 usando OpenSSL EVP",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__hash(void) {
    return PyModule_Create(&module);
}

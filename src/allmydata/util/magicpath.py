# from the Python Standard Library
import string

def magic2path(path):
    path = string.replace(path, "@@", "|")
    path = string.replace(path, "@", "/")
    path = string.replace(path, "|", "@")
    return path

def path2magic(path):
    path = string.replace(path, "@", "@@")
    path = string.replace(path, "/", "@")
    return path

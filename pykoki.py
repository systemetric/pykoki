from ctypes import *
import os
from v4l2 import v4l2

KOKI_MARKER_GRID_WIDTH = 10


### stdint datatypes ###
class uint8(c_ubyte):

    def __repr__(self):
        return "uint8 (%d)" % (self.value)


class uint16(c_ushort):

    def __repr__(self):
        return "uint16 (%d)" % (self.value)


### GLib structs ###

# GLib 'primitive' datatypes
class gchar_p(c_char_p): pass
class guint(c_uint): pass
class gpointer(c_void_p): pass


class GArray(Structure):

    _fields_ = [("data", gchar_p), ("len", guint)]


class GSList(Structure): pass
GSList._fields_ = [("data", gpointer), ("next", POINTER(GSList))]



class Bearing(Structure):

    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]

    def __repr__(self):
        return "Bearing (x=%f, y=%f, z=%f)" % (self.x, self.y, self.z)



class Point2Di(Structure):

    _fields_ = [("x", c_int), ("y", c_int)]

    def __repr__(self):
        return "Point2Di (x=%i, y=%i)" % (self.x, self.y)



class Point2Df(Structure):

    _fields_ = [("x", c_float), ("y", c_float)]

    def __repr__(self):
        return "Point2Df (x=%f, y=%f)" % (self.x, self.y)



class Point3Df(Structure):

    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]

    def __repr__(self):
        return "Point3Df (x=%f, y=%f, z=%f)" % (self.x, self.y, self.z)



class MarkerVertex(Structure):

    _fields_ = [("image", Point2Df), ("world", Point3Df)]

    def __repr__(self):
        return "Marker Vertex (image = %s, world = %s)" % (self.image, self.world)


class MarkerRotation(Structure):

    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]

    def __repr__(self):
        return "MarkerRotation (x=%f, y=%f, z=%f)" % (self.x, self.y, self.z)



class Marker(Structure):

    _fields_ = [("code", c_int), ("centre", MarkerVertex), ("bearing", Bearing),
                ("distance", c_float), ("rotation", MarkerRotation),
                ("rotation_offset", c_float), ("vertices", MarkerVertex * 4)]

    def __repr__(self):
        return "Marker (\n\tcode=%d,\n\tcentre = %s,\n\tbearing = %s,\n\tdistance=%f,\n\trotation = %s,\n\trotation_offset=%f,\n\tvertices = [\n\t\t%s,\n\t\t%s,\n\t\t%s,\n\t\t%s])" % (self.code, self.centre, self.bearing, self.distance, self.rotation, self.rotation_offset, self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3])



class ClipRegion(Structure):

    _fields_ = [("mass", c_int), ("min", Point2Di), ("max", Point2Di)]

    def __repr__(self):
        return "ClipRegion (mass=%d, min = %s, max = %s)" % (self.mass, self.min, self.max)



class Cell(Structure):

    _fields_ = [("num_pixels", c_int), ("sum", c_int), ("val", c_int)]

    def __repr__(self):
        return "Cell (num_pixels=%d, sum=%d, val=%d)" % (self.num_pixels, self.sum, self.val)


Grid = (Cell * KOKI_MARKER_GRID_WIDTH) * KOKI_MARKER_GRID_WIDTH

def GridRepr(self):
    ret = "Grid:\n["
    for i in range(KOKI_MARKER_GRID_WIDTH):
        ret += "["
        for j in range(KOKI_MARKER_GRID_WIDTH):
            ret += "(%d, %d, %d),\t" % (self[i][j].num_pixels, self[i][j].sum, self[i][j].val)
        ret = ret[:-3]
        ret += "],\n "

    ret = ret[:-3]
    ret += "]"
    return ret

Grid.__repr__ = GridRepr



class CameraParams(Structure):

    _fields_ = [("focal_length", Point2Df), ("principal_point", Point2Df), ("size", Point2Di)]

    def __repr__(self):
        return "CameraParams (focal_length = %s, principal_point = %s, size = %s)" % (self.focal_length, self.principal_point, self.size)



class Quad(Structure):

    _fields_ = [("links", POINTER(GSList) * 4), ("vertices", Point2Df * 4)]

    def __repr__(self):

        return "Quad (links = [%s, %s, %s, %s], vertices = [%s, %s, %s, %s])" % (self.links[0], self.links[1], self.links[2], self.links[3], self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3])



class LabelledImage(Structure):

    _fields_ = [("aliases", POINTER(GArray)), ("clips", POINTER(GArray)),
                ("data", POINTER(uint16)), ("h", uint16), ("w", uint16)]

    def __repr__(self):

        return "LabelledImage (aliases = %s, clips = %s, data = %s, w=%s, h=%s)" % (self.aliases, self.clips, self.data, self.w, self.h)


class Buffer(Structure):

    _fields_ = [("length", c_size_t), ("start", POINTER(uint8))]

    def __repr__(self):

        return "Buffer (length=%s, start = %s)" % (self.length, self.start)




class PyKoki:

    def __init__(self):

        self._load_library("../libkoki/lib/")
        self._setup_library()



    def _load_library(self, directory):

        libkoki = None

        path = os.path.join(directory, "libkoki.so")

        if os.path.exists(path):
            libkoki = cdll.LoadLibrary(path)

        if libkoki == None:
            raise Exception("pykoki: libkoki.so not found")

        self.libkoki = libkoki



    def _setup_library(self):

        l = self.libkoki

        ### v4l.h ###

        # int koki_v4l_open_cam(const char* filename)
        l.koki_v4l_open_cam.argtypes = [c_char_p]
        l.koki_v4l_open_cam.resytpe = c_int

        # void koki_v4l_close_cam(int fd)
        l.koki_v4l_close_cam.argtypes = [c_int]

        # struct v4l2_format koki_v4l_get_format()
        l.koki_v4l_get_format.argtypes = [c_int]
        l.koki_v4l_get_format.restype = v4l2.v4l2_format

        # int koki_v4l_set_format(int fd, struct v4l2_format fmt)
        l.koki_v4l_set_format.argtypes = [c_int, v4l2.v4l2_format]
        l.koki_v4l_set_format.restype = c_int


        ### crc12.h ###

        # uint16_t koki_crc12 (uint8_t input)
        l.koki_crc12.argtypes = [uint8]
        l.koki_crc12.restype = uint16



    def v4l_open_cam(self, filename):

        return self.libkoki.koki_v4l_open_cam(filename)


    def v4l_close_cam(self, fd):

        return self.libkoki.koki_v4l_close_cam(fd)


    def v4l_get_format(self, fd):

        return self.libkoki.koki_v4l_get_format(fd)


    def v4l_set_format(self, fd, fmt):

        return self.libkoki.koki_v4l_set_format(fd, fmt)


    def crc12(self, n):

        return self.libkoki.koki_crc12(n)

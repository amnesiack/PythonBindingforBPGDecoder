#!/usr/bin/env python3
from PIL import Image
from glob import glob
import os
import math
import tensorflow as tf
import numpy as np
import scipy.io as scio
from ctypes import *
from enum import Enum

################################
# BPG Decoder Python Binding
################################
DLL = cdll.LoadLibrary('./libbpg.so')

class BPGDecoderContext(Structure):
    pass

class BPGImageFormatEnum(Enum):
    (
    BPG_FORMAT_GRAY,
    BPG_FORMAT_420,
    BPG_FORMAT_422,
    BPG_FORMAT_444,
    BPG_FORMAT_420_VIDEO,
    BPG_FORMAT_422_VIDEO,
    )=range(6)

class BPGColorSpaceEnum(Enum):
    (
    BPG_CS_YCbCr,
    BPG_CS_RGB,
    BPG_CS_YCgCo,
    BPG_CS_YCbCr_BT709,
    BPG_CS_YCbCr_BT2020,
    BPG_CS_COUNT,
    )=range(6)

class BPGImageInfo(Structure):
    _fields_ = [
        ("width", c_int),
        ("height", c_int),
        ("format", c_int),
        ("has_alpha", c_int),
        ("color_space", c_int),
        ("bit_depth", c_int),
        ("premultiplied_alpha", c_int),
        ("has_w_plane", c_int),
        ("limited_range", c_int),
        ("has_animation", c_int),
        ("loop_count", c_int),
    ]

class BPGExtensionTagEnum(Enum):
    BPG_EXTENSION_TAG_EXIF = 1,
    BPG_EXTENSION_TAG_ICCP = 2,
    BPG_EXTENSION_TAG_XMP = 3,
    BPG_EXTENSION_TAG_THUMBNAIL = 4,
    BPG_EXTENSION_TAG_ANIM_CONTROL = 5,

class BPGExtensionData(Structure):
    pass

BPGExtensionData._fields_ = [
        ("tag", c_uint8),
        ("buf_len", c_uint32),
        ("buf", POINTER(c_uint8)),
        ("next", POINTER(BPGExtensionData))
    ]

class BPGDecoderOutputFormat(Enum):
    (
    BPG_OUTPUT_FORMAT_RGB24,
    BPG_OUTPUT_FORMAT_RGBA32,
    BPG_OUTPUT_FORMAT_RGB48,
    BPG_OUTPUT_FORMAT_RGBA64,
    BPG_OUTPUT_FORMAT_CMYK32,
    BPG_OUTPUT_FORMAT_CMYK64,
    )=range(6)

BPG_DECODER_INFO_BUF_SIZE = 16

######################################
#        define the functions                                                               #
######################################
_bpg_decoder_open=DLL.bpg_decoder_open
_bpg_decoder_open.argtypes=None
_bpg_decoder_open.restype=POINTER(BPGDecoderContext)
def bpg_decoder_open():
    return _bpg_decoder_open()


_bpg_decoder_keep_extension_data=DLL.bpg_decoder_keep_extension_data
_bpg_decoder_keep_extension_data.argtypes=[POINTER(BPGDecoderContext), c_int]
_bpg_decoder_keep_extension_data.restype=None
def bpg_decoder_keep_extension_data(s, enable):
    _bpg_decoder_keep_extension_data(s, enable)


_bpg_decoder_decode=DLL.bpg_decoder_decode
_bpg_decoder_decode.argtypes=[POINTER(BPGDecoderContext), POINTER(c_uint8), c_int]
_bpg_decoder_decode.restype=c_int
def bpg_decoder_decode(s, buf, buf_len):
    buf=cast(buf, POINTER(c_uint8))
    return _bpg_decoder_decode(s, buf, buf_len)


_bpg_decoder_get_extension_data=DLL.bpg_decoder_get_extension_data
_bpg_decoder_get_extension_data.argtypes=[POINTER(BPGDecoderContext)]
_bpg_decoder_get_extension_data.restype=POINTER(BPGDecoderContext)
def bpg_decoder_get_extension_data(s):
    return _bpg_decoder_get_extension_data(s)


_bpg_decoder_get_info=DLL.bpg_decoder_get_info
_bpg_decoder_get_info.argtypes=[POINTER(BPGDecoderContext), POINTER(BPGImageInfo)]
_bpg_decoder_get_info.restype=c_int
def bpg_decoder_get_info(s, p):
    return _bpg_decoder_get_info(s, p)


_bpg_decoder_start = DLL.bpg_decoder_start
_bpg_decoder_start.argtypes=[POINTER(BPGDecoderContext), c_int]
_bpg_decoder_start.restype=c_int
def bpg_decoder_start(s, out_fmt):
    return _bpg_decoder_start(s, out_fmt)


_bpg_decoder_get_line=DLL.bpg_decoder_get_line
_bpg_decoder_get_line.argtypes=[POINTER(BPGDecoderContext), c_void_p]
_bpg_decoder_get_line.restype=c_int
def bpg_decoder_get_line(s, buf):
    buf=cast(buf, c_void_p)
    return _bpg_decoder_get_line(s, buf)


_bpg_decoder_close=DLL.bpg_decoder_close
_bpg_decoder_close.argtypes=[POINTER(BPGDecoderContext)]
_bpg_decoder_close.restype=None
def bpg_decoder_close(s):
    _bpg_decoder_close(s)


_bpg_decoder_get_data=DLL.bpg_decoder_get_data
_bpg_decoder_get_data.argtypes=[POINTER(BPGDecoderContext), POINTER(c_int), c_int]
_bpg_decoder_get_data.restype=POINTER(c_uint8)
def bpg_decoder_get_data(s, pline_size, plane):
    return _bpg_decoder_get_data(s, pline_size, plane)


_bpg_decoder_get_info_from_buf=DLL.bpg_decoder_get_info_from_buf
_bpg_decoder_get_info_from_buf.argtypes=[POINTER(BPGImageInfo),
                                  POINTER(POINTER(BPGExtensionData)),
                                  POINTER(c_uint8), c_int]
_bpg_decoder_get_info_from_buf.restype=c_int
def bpg_decoder_get_info_from_buf(p,
                                  pfirst_md,
                                  buf, buf_len
                                  ):
    return _bpg_decoder_get_info_from_buf(p,
                                  pfirst_md,
                                  buf, buf_len
                                  )


_bpg_decoder_free_extension_data=DLL.bpg_decoder_free_extension_data
_bpg_decoder_free_extension_data.argtypes=[POINTER(BPGExtensionData)]
_bpg_decoder_free_extension_data.restype=None
def bpg_decoder_free_extension_data(first_md):
    _bpg_decoder_free_extension_data(first_md)
##############

def ppm_save(img):
    #img_info_s = POINTER(BPGImageInfo)
    img_info = BPGImageInfo()
    bpg_decoder_get_info(img, img_info)
    w = img_info.width
    h = img_info.height
    rgb_line = create_string_buffer(sizeof(c_uint8)*(3*w))
    bpg_decoder_start(img, 0)
    BPGdec = np.zeros([h, w*3], dtype='float32')
    for y in range(h):
        bpg_decoder_get_line(img, rgb_line)
        BPGdec[y, :] = np.frombuffer(rgb_line, dtype = 'uint8')
    BPG_R = BPGdec[:,::3]
    BPG_R = np.expand_dims(BPG_R, -1)
    BPG_G = BPGdec[:,1::3]
    BPG_G = np.expand_dims(BPG_G, -1)
    BPG_B = BPGdec[:,2::3]
    BPG_B = np.expand_dims(BPG_B, -1)
    BPG_dec_out = np.concatenate((BPG_R, BPG_G, BPG_B),2)
    return BPG_dec_out
def Mybpgdec(filename):
    f = open(filename, 'rb')
    buf_len = os.stat(filename)[6]
    buf = f.read()
    f.close()

    img = bpg_decoder_open()

    if (bpg_decoder_decode(img, buf, buf_len) < 0):
        print("Could not decode image\n")
        os.exit(1)

    BPG_dec_out = ppm_save(img)
    bpg_decoder_close(img)
    return BPG_dec_out

# Image Reading
for image_file in glob('./*.bpg'):
    image1 = Mybpgdec(image_file)
    image1 = image1.astype(np.uint8)
    rec   = Image.fromarray(image1)
    rec.save(image_file[:-4]+'.png')

#!/usr/bin/env python

import numpy as np
import tensorflow as tf
import cv2
import os,sys
sys.path.insert(1, os.path.join(sys.path[0], '/mywork/tensorflow-tuts/sd19reader'))
from myutils import describe

#---------------------------------------------------------------------
# load library
path2file = os.path.dirname(os.path.realpath(__file__))
builtlibpath_dir = os.path.join(path2file, '../build/lib')
builtlibpath = os.path.join(builtlibpath_dir, 'libtfgaussiancrf.so')
libtfgaussiancrf = tf.load_op_library(builtlibpath)

print("-----------------------------------")
from inspect import getmembers, isfunction
functions_list = [o for o in getmembers(libtfgaussiancrf) if isfunction(o[1])]
print(str(functions_list))
print("-----------------------------------")

#---------------------------------------------------------------------
# setup a test

def NHWC_to_NCHW(arr):
    return arr.transpose((0,3,1,2))
def NCHW_to_NHWC(arr):
    return arr.transpose((0,2,3,1))

# cv2 image read shape: (height, width, channels)
# tensorflow conv2d image shape: (batch, height, width, channels)
catfile = os.path.join(path2file,'cat.jpg')
catim = cv2.imread(catfile,cv2.IMREAD_COLOR).astype(np.float32) / 255.0
catim = catim.reshape([1,]+list(catim.shape))

tfcatplaceholder = tf.placeholder(tf.float32, [None,None,None,None], name="tfcatplaceholder")

npwspatial = np.expand_dims(np.expand_dims(np.eye(catim.shape[-1]),0),0).astype(np.float32)
npwbilateral = npwspatial.copy()

tfwspatial   = tf.constant(npwspatial)
tfwbilateral = tf.constant(npwbilateral)

'''
.Input("input: T")
.Input("featswrt: T")
.Input("wspatial: T")
.Input("wbilateral: T")
.Attr("stdv_spatial_space: float = 1.0")
.Attr("stdv_bilater_space: float = 1.0")
'''

copycat  = libtfgaussiancrf.bilateral_filters(tfcatplaceholder,
                                              tfcatplaceholder,
                                              tfwspatial,
                                              tfwbilateral,
                                              1.0,
                                              1.0)

print("constructed the filter!!!!!!!!!!!!!!!!!!!!!!")
describe("catim",catim)
describe("tfwspatial",tfwspatial)
describe("tfwbilateral",tfwbilateral)
print("\n")

#---------------------------------------------------------------------
# run the test

sess = tf.InteractiveSession()

tf.initialize_all_variables().run()

npcopycat = NCHW_to_NHWC(copycat.eval({tfcatplaceholder: NHWC_to_NCHW(catim)}))

describe("catim",catim)
describe("npcopycat",npcopycat)
cv2.imshow("catim",catim[0,...])
cv2.imshow("npcopycat",npcopycat[0,...])
cv2.waitKey(0)
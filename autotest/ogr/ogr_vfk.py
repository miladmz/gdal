#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test OGR VFK driver functionality.
# Author:   Martin Landa <landa.martin gmail.com>
#
###############################################################################
# Copyright (c) 2009-2018 Martin Landa <landa.martin gmail.com>
# Copyright (c) 2010-2012, Even Rouault <even dot rouault at mines-paris dot org>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

import os
import sys

sys.path.append('../pymod')

import gdaltest
from osgeo import gdal
from osgeo import ogr

###############################################################################
# Open file, check number of layers, get first layer,
# check number of fields and features


def ogr_vfk_1():

    gdaltest.vfk_drv = ogr.GetDriverByName('VFK')
    if gdaltest.vfk_drv is None:
        return 'skip'

    try:
        os.remove('data/bylany.vfk.db')
    except OSError:
        pass

    gdaltest.vfk_ds = ogr.Open('data/bylany.vfk')

    if gdaltest.vfk_ds is None:
        return 'fail'

    if gdaltest.vfk_ds.GetLayerCount() != 61:
        gdaltest.post_reason('expected exactly 61 layers!')
        return 'fail'

    gdaltest.vfk_layer_par = gdaltest.vfk_ds.GetLayer(0)

    if gdaltest.vfk_layer_par is None:
        gdaltest.post_reason('cannot get first layer')
        return 'fail'

    if gdaltest.vfk_layer_par.GetName() != 'PAR':
        gdaltest.post_reason('did not get expected layer name "PAR"')
        return 'fail'

    defn = gdaltest.vfk_layer_par.GetLayerDefn()
    if defn.GetFieldCount() != 28:
        gdaltest.post_reason('did not get expected number of fields, got %d' % defn.GetFieldCount())
        return 'fail'

    fc = gdaltest.vfk_layer_par.GetFeatureCount()
    if fc != 1:
        gdaltest.post_reason('did not get expected feature count, got %d' % fc)
        return 'fail'

    return 'success'

###############################################################################
# Read the first feature from layer 'PAR', check envelope


def ogr_vfk_2():

    if gdaltest.vfk_drv is None:
        return 'skip'

    gdaltest.vfk_layer_par.ResetReading()

    feat = gdaltest.vfk_layer_par.GetNextFeature()

    if feat.GetFID() != 1:
        gdaltest.post_reason('did not get expected fid for feature 1')
        return 'fail'

    geom = feat.GetGeometryRef()
    if geom.GetGeometryType() != ogr.wkbPolygon:
        gdaltest.post_reason('did not get expected geometry type.')
        return 'fail'

    envelope = geom.GetEnvelope()
    area = (envelope[1] - envelope[0]) * (envelope[3] - envelope[2])
    exp_area = 2010.5

    if area < exp_area - 0.5 or area > exp_area + 0.5:
        gdaltest.post_reason('envelope area not as expected, got %g.' % area)
        return 'fail'

    return 'success'

###############################################################################
# Read features from layer 'SOBR', test attribute query


def ogr_vfk_3():

    if gdaltest.vfk_drv is None:
        return 'skip'

    gdaltest.vfk_layer_sobr = gdaltest.vfk_ds.GetLayer(43)

    if gdaltest.vfk_layer_sobr.GetName() != 'SOBR':
        gdaltest.post_reason('did not get expected layer name "SOBR"')
        return 'fail'

    gdaltest.vfk_layer_sobr.SetAttributeFilter("CISLO_BODU = '55'")

    gdaltest.vfk_layer_sobr.ResetReading()

    feat = gdaltest.vfk_layer_sobr.GetNextFeature()
    count = 0
    while feat:
        feat = gdaltest.vfk_layer_sobr.GetNextFeature()
        count += 1

    if count != 1:
        gdaltest.post_reason('did not get expected number of features, got %d' % count)
        return 'fail'

    return 'success'

###############################################################################
# Read features from layer 'SBP', test random access, check length


def ogr_vfk_4():

    if gdaltest.vfk_drv is None:
        return 'skip'

    gdaltest.vfk_layer_sbp = gdaltest.vfk_ds.GetLayerByName('SBP')

    if not gdaltest.vfk_layer_sbp:
        gdaltest.post_reason('did not get expected layer name "SBP"')
        return 'fail'

    feat = gdaltest.vfk_layer_sbp.GetFeature(5)
    length = int(feat.geometry().Length())

    if length != 10:
        gdaltest.post_reason('did not get expected length, got %d' % length)
        return 'fail'

    return 'success'

###############################################################################
# Read features from layer 'HP', check geometry type


def ogr_vfk_5():

    if gdaltest.vfk_drv is None:
        return 'skip'

    gdaltest.vfk_layer_hp = gdaltest.vfk_ds.GetLayerByName('HP')

    if not gdaltest.vfk_layer_hp != 'HP':
        gdaltest.post_reason('did not get expected layer name "HP"')
        return 'fail'

    geom_type = gdaltest.vfk_layer_hp.GetGeomType()

    if geom_type != ogr.wkbLineString:
        gdaltest.post_reason('did not get expected geometry type, got %d' % geom_type)
        return 'fail'

    return 'success'

###############################################################################
# Re-Open file (test .db persistence)


def ogr_vfk_6():

    if gdaltest.vfk_drv is None:
        return 'skip'

    gdaltest.vfk_layer_par = None
    gdaltest.vfk_layer_sobr = None
    gdaltest.vfk_ds = None
    gdaltest.vfk_ds = ogr.Open('data/bylany.vfk')

    if gdaltest.vfk_ds is None:
        return 'fail'

    if gdaltest.vfk_ds.GetLayerCount() != 61:
        gdaltest.post_reason('expected exactly 61 layers!')
        return 'fail'

    gdaltest.vfk_layer_par = gdaltest.vfk_ds.GetLayer(0)

    if gdaltest.vfk_layer_par is None:
        gdaltest.post_reason('cannot get first layer')
        return 'fail'

    if gdaltest.vfk_layer_par.GetName() != 'PAR':
        gdaltest.post_reason('did not get expected layer name "PAR"')
        return 'fail'

    defn = gdaltest.vfk_layer_par.GetLayerDefn()
    if defn.GetFieldCount() != 28:
        gdaltest.post_reason('did not get expected number of fields, got %d' % defn.GetFieldCount())
        return 'fail'

    fc = gdaltest.vfk_layer_par.GetFeatureCount()
    if fc != 1:
        gdaltest.post_reason('did not get expected feature count, got %d' % fc)
        return 'fail'

    return 'success'

###############################################################################
# Read PAR layer, check data types (Integer64 new in GDAL 2.2)


def ogr_vfk_7():

    if gdaltest.vfk_drv is None:
        return 'skip'

    defn = gdaltest.vfk_layer_par.GetLayerDefn()

    for idx, name, ctype in ((0, "ID", ogr.OFTInteger64),
                             (1, "STAV_DAT", ogr.OFTInteger),
                             (2, "DATUM_VZNIKU", ogr.OFTString),
                             (22, "CENA_NEMOVITOSTI", ogr.OFTReal)):
        col = defn.GetFieldDefn(idx)
        if col.GetName() != name or col.GetType() != ctype:
            gdaltest.post_reason("PAR: '{}' column name/type mismatch".format(name))
            return 'fail'

    return 'success'

###############################################################################
# Open DB file as datasource (new in GDAL 2.2)


def ogr_vfk_8():

    if gdaltest.vfk_drv is None:
        return 'skip'

    # open by SQLite driver first
    vfk_ds_db = ogr.Open('data/bylany.db')
    count1 = vfk_ds_db.GetLayerCount()
    vfk_ds_db = None

    # then open by VFK driver
    os.environ['OGR_VFK_DB_READ'] = 'YES'
    vfk_ds_db = ogr.Open('data/bylany.db')
    count2 = vfk_ds_db.GetLayerCount()
    vfk_ds_db = None

    if count1 != count2:
        gdaltest.post_reason('layer count differs when opening DB by SQLite and VFK drivers')
        return 'fail'

    del os.environ['OGR_VFK_DB_READ']

    return 'success'

###############################################################################
# Open datasource with SUPPRESS_GEOMETRY open option (new in GDAL 2.3)


def ogr_vfk_9():

    if gdaltest.vfk_drv is None:
        return 'skip'

    # open with suppressing geometry
    vfk_ds = None
    vfk_ds = gdal.OpenEx('data/bylany.vfk', open_options=['SUPPRESS_GEOMETRY=YES'])

    vfk_layer_par = vfk_ds.GetLayerByName('PAR')

    if not vfk_layer_par != 'PAR':
        gdaltest.post_reason('did not get expected layer name "PAR"')
        return 'fail'

    geom_type = vfk_layer_par.GetGeomType()
    vfk_layer_par = None
    vfk_ds = None

    if geom_type != ogr.wkbNone:
        gdaltest.post_reason('did not get expected geometry type, got %d' % geom_type)
        return 'fail'

    return 'success'

###############################################################################
# Open datasource with FILE_FIELD open option (new in GDAL 2.4)


def ogr_vfk_10():

    if gdaltest.vfk_drv is None:
        return 'skip'

    # open with suppressing geometry
    vfk_ds = None
    vfk_ds = gdal.OpenEx('data/bylany.vfk', open_options=['FILE_FIELD=YES'])

    vfk_layer_par = vfk_ds.GetLayerByName('PAR')

    if not vfk_layer_par != 'PAR':
        gdaltest.post_reason('did not get expected layer name "PAR"')
        return 'fail'

    vfk_layer_par.ResetReading()
    feat = vfk_layer_par.GetNextFeature()
    file_field = feat.GetField('VFK_FILENAME')
    vfk_layer_par = None
    vfk_ds = None

    if file_field != 'bylany.vfk':
        gdaltest.post_reason('did not get expected file field value')
        return 'fail'

    return 'success'

###############################################################################
# Read PAR layer, check sequential feature access consistency


def ogr_vfk_11():
    def count_features():
        gdaltest.vfk_layer_par.ResetReading()
        count = 0
        while True:
            feat = gdaltest.vfk_layer_par.GetNextFeature()
            if not feat:
                break
            count += 1

        return count

    if gdaltest.vfk_drv is None:
        return 'skip'

    count = gdaltest.vfk_layer_par.GetFeatureCount()
    for i in range(2): # perform check twice, mix with random access
        if count != count_features():
            feat = gdaltest.vfk_layer_par.GetFeature(i)
            gdaltest.post_reason('did not get expected number of features')
            return 'fail'

    return 'success'

###############################################################################
# cleanup


def ogr_vfk_cleanup():

    if gdaltest.vfk_drv is None:
        return 'skip'

    gdaltest.vfk_layer_par = None
    gdaltest.vfk_layer_hp = None
    gdaltest.vfk_layer_sobr = None
    gdaltest.vfk_ds = None

    try:
        os.remove('data/bylany.db')
    except OSError:
        pass

    return 'success'

###############################################################################
#


gdaltest_list = [
    ogr_vfk_1,
    ogr_vfk_2,
    ogr_vfk_3,
    ogr_vfk_4,
    ogr_vfk_5,
    ogr_vfk_6,
    ogr_vfk_7,
    ogr_vfk_8,
    ogr_vfk_9,
    ogr_vfk_10,
    ogr_vfk_11,
    ogr_vfk_cleanup]

if __name__ == '__main__':
    gdaltest.setup_run('ogr_vfk')

    gdaltest.run_tests(gdaltest_list)

    gdaltest.summarize()

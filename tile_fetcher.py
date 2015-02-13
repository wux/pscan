#!/usr/bin/env python
# encoding: utf-8

"""                                                                                  
Raster tile fetcher.

This utility takes in a lat lng bounding box and fetch all the raster tiles.

Example:
  python tile_fetcher.py 17 37.547614 37.555508 -122.25729700000001 -122.266524\
         /tmp/test.jpg

Author : James X. Wu

"""

import os
import math
import sys
import subprocess
import urllib2
import logging

import Image
import ImageFile


SERVER = 'http://raster-test.dev.geo.apple.com'
TILE_SIZE = 256


def fetchTile(server, z, x, y):
    url = '%s/ctile?style=7&v=1&scale=1&size=1' % server
    url += '&md=backgroundMapnik2&z=%d&x=%d&y=%d' % (z, x, y)
    logging.info('Fetching tile at: %s' % url)
    tile = urllib2.urlopen(url)
    parser = ImageFile.Parser()
    parser.feed(tile.read())
    im = parser.close()
    return im


def mosaicTiles(tiles, numRow, numCol):
    mosaic = Image.new("RGB", (numCol * TILE_SIZE, numRow * TILE_SIZE))
    numTiles = 0
    for tile in tiles:
        offsetX = numTiles % numCol * TILE_SIZE
        offsetY = numTiles / numCol * TILE_SIZE
        mosaic.paste(tile, (offsetX, offsetY))
        logging.debug('%d %d %d' %(numTiles, offsetX, offsetY))
        numTiles += 1

    return mosaic


def lng2PixelX(zoom, lng):
    return int((lng + 180.0) / 360.0 * TILE_SIZE * math.pow(2, zoom))


def lat2PixelY(zoom, lat):
    sinLat = math.sin(lat * math.pi / 180.0)
    return int((0.5 - math.log((1 + sinLat) / (1 - sinLat)) / (4 * math.pi)) *
               TILE_SIZE * math.pow(2, zoom))


def lng2TileX(zoom, lng):
    return int((lng + 180.0) / 360.0 * math.pow(2, zoom))


def lat2TileY(zoom, lat):
    sinLat = math.sin(lat * math.pi / 180.0)
    return int((0.5 - math.log((1 + sinLat) / (1 - sinLat)) / (4 * math.pi)) *
               math.pow(2, zoom))
    

def buildMosaic(z, nsew, doCrop = True):
    (n, s, e, w) = nsew
    tiles = []
    min_x = lng2TileX(z, w)
    max_x = lng2TileX(z, e)
    max_y = lat2TileY(z, n)
    min_y = lat2TileY(z, s)
    logging.debug('%d, %d, %d, %d' % (min_x, max_x, min_y, max_y))
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            tiles.append(fetchTile(SERVER, z, x, y))
    numRow = max_y - min_y + 1
    numCol = max_x - min_x + 1
    mosaic = mosaicTiles(tiles, numRow, numCol)
    if doCrop:
        min_pixel_x = lng2PixelX(z, w) % TILE_SIZE
        max_pixel_x = numCol * TILE_SIZE - lng2PixelX(z, e) % TILE_SIZE
        min_pixel_y = lat2PixelY(z, s) % TILE_SIZE
        max_pixel_y = numRow * TILE_SIZE - lat2PixelY(z, n) % TILE_SIZE
        # (left, top, right, bottom)
        bbox = (min_pixel_x, min_pixel_y, max_pixel_x, max_pixel_y)
        print 'Original image bbox: '
        print mosaic.getbbox()
        print 'Cropping bbox: '
        print bbox

        roi = mosaic.crop(bbox)
        return roi
    else:
        return mosaic


if not len(sys.argv) > 6:
    raise SystemExit("Usage: %s <zoom> <north> <south> <east> <west> <file>")

nsew = [float(x) for x in sys.argv[2:-1]]
print nsew

mosaic = buildMosaic(int(sys.argv[1]), nsew, doCrop = True)
# mosaic.show()
mosaic.save(sys.argv[6], 'JPEG')

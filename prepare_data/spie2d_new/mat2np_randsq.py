#!/usr/bin/env python

import glob
import argparse
import sys
import os

# load mat in python
import scipy.io as spio
import numpy as np



#------------------------------------------------------------------------------
# 
#------------------------------------------------------------------------------
def gen_data(photon_vol='1e+05', batch_size = 64, im_w = 100, im_h = 100,
                 data_dir='../../data/spie2d_new/randsq',
                 clean_dir ='../../data/spie2d_new/randsq/1e+07',
                 clean_prefix='test',
                 save_dir = '../../model_input/spie2d_new/'):
    '''
    Each simulation results in a different 2D voxel image  using different random seed.
    '''

    #--------------------------------------------------------------------------
    # count the number of patches
    #--------------------------------------------------------------------------
    target_dir = data_dir + '/' + photon_vol  # locate the simulation folder
    dir_files = target_dir + '/*.mat'
    filepaths_dir = glob.glob(dir_files)    # form the file path
    img_count = len(filepaths_dir)

    print "[LOG] There are %d images." % img_count

    #--------------------------------------------------------------------------
    # 
    # 
    #--------------------------------------------------------------------------

    if img_count % batch_size != 0:  # if can't be evenly dived by batch size
        numPatches = (img_count / batch_size + 1) * batch_size 
    else:
        numPatches = img_count

    print "[LOG] total patches = %d , batch size = %d, total batches = %d" % \
          (numPatches, batch_size, numPatches / batch_size)



    #--------------------------------------------
    # data matrix 4-D : model input and output 
    #--------------------------------------------
    inputs_noisy = np.zeros((numPatches, im_w, im_h, 1), dtype=np.float32) 
    inputs_clean = np.zeros((numPatches, im_w, im_h, 1), dtype=np.float32)


    #--------------------------------------------------------------------------
    # generate the patches
    #--------------------------------------------------------------------------
    imgNum = 0

    files_in_dir = target_dir + '/*.mat'
    filepaths_ = glob.glob(files_in_dir)
    imgprefix_ = target_dir + '/' +  'test'

    #print imgprefix_

    #----------------------------------------------------------------------
    # files for images
    #----------------------------------------------------------------------
    imgNum = len(filepaths_)

    for fid, noisyfile in enumerate(filepaths_):
        noisymat = spio.loadmat(noisyfile, squeeze_me=True)
        noisyData = noisymat['currentImage']

        #-------------------------------------------
        # find out the imageID
        # remove the prefix, then the suffix ".mat"
        #-------------------------------------------
        img_prefix_len = len(imgprefix_)
        img_id = int(noisyfile[img_prefix_len:][:-4])

        cleanfile = clean_dir + '/' + clean_prefix + str(img_id) + '.mat'

        #print noisyfile
        #print cleanfile
        #break


        cleanmat = spio.loadmat(cleanfile, squeeze_me=True)
        cleanData = cleanmat['currentImage']

        if noisyData.shape[0] != cleanData.shape[0] or noisyData.shape[1] != cleanData.shape[1]:
            print('Error! Noisy data size is different from clean data size!')
            sys.exit(1)


        # extend one dimension
        noisyData = np.reshape(noisyData, (im_w, im_h, 1))
        cleanData = np.reshape(cleanData, (im_w, im_h, 1))

        ## print noisyData.shape
        
        #
        # update noisy and clean array
        #
        inputs_noisy[fid, :, :, :] = noisyData[:, :, :]
        inputs_clean[fid, :, :, :] = cleanData[:, :, :]


    patch_count = imgNum
    print '[LOG] %d images are generated!' % (patch_count)


    #print inputs_noisy[10, 50, 50, :],  inputs_clean[10, 50, 50, :]


    #--------------------------------------------------------------------------
    # pad the array 
    #--------------------------------------------------------------------------
    if patch_count < numPatches:
        print '[LOG] padding the batch ... '
        to_pad = numPatches - patch_count
        inputs_noisy[-to_pad:, :, :, :] = inputs_noisy[:to_pad, :, :, :]
        inputs_clean[-to_pad:, :, :, :] = inputs_clean[:to_pad, :, :, :]


    #--------------------------------------------------------------------------
    # save it to a file 
    #--------------------------------------------------------------------------
    print '[LOG] saving data to disk ... '
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    np.save(os.path.join(save_dir, "randsq_p5"), inputs_noisy)
    np.save(os.path.join(save_dir, "randsq_p7"), inputs_clean)

    print '[LOG] Done! '
    print '[LOG] Check %s for the output.' % save_dir
    print "[LOG] size of inputs tensor = " + str(inputs_noisy.shape)


if __name__ == '__main__':
    print '\nGenerating rand2d data.'
    gen_data()

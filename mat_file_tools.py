# This is a library of tools for use in reading mat files into python.
# 
# Written by Jim Rafferty: james.m.rafferty@gmail.com
#
################################# Available functions #################################
#
# load_data(data_file, vars_in = None)
# get_variable_list(data_file)
#
# data_to_dict(hdf5_data)
# cell_to_list(hdf5_data, data_file = None)
#
#######################################################################################
#
#### load_data(data_file, vars_in = None)
# 
# This is the basic function that reads a mat file and returns a dict containing data
#
# Inputs: data_file - a string with the path to a mat file
#         vars_in - a list of strings with variable names to load in. If this is None, 
#                   all variables are read in.
#
# Outputs: data - a dict containing data. Each matlab variable is reference by name (string)
#
##### get_variable_list(data_file)
#
# This function finds the variable names stored in a mat file.
#
# Inputs: data_file - a string with the path to a mat file
#
# Outputs: var_list - a list of strings containing variable names.
#
##### data_to_dict(hdf5_data)
#
# Internal function used to read hdf5 mat file data into a dict.
#
##### cell_to_list(hdf5_data, data_file = None)
#
# Internal function used to dereference a matlab cell array into a list.
#
#######################################################################################

import scipy.io as sio
import h5py as hio
from numpy import object_, reshape, prod, shape

def string(seq):
	#Convert a sequence of integers into a single string.
	return ''.join([chr(a) for a in seq])

def load_data(data_file, vars_in = None):

	try:
		data = sio.loadmat(data_file, variable_names = vars_in) 
		# TODO: get index structure of outputs to match for unicode and hdf5
		# TODO: add other useful optional arguments for sio.loadmat and code below.
	except NotImplementedError:
		h_keys = get_variable_list(data_file)
		if vars_in == None: 
			keys_sel = h_keys
		else:
			keys_sel = vars_in
		data_h = hio.File(data_file, 'r')
		data = {}
		for k in h_keys: 
			if k in keys_sel:
				data[k] = data_to_dict(data_h[k])

	return data

def get_variable_list(data_file):

	try:
		data = sio.loadmat(data_file)
		var_list = []
		for k in data.keys():
			if k[0] != '_':
				var_list.append(k)
	except NotImplementedError:
		data = hio.File(data_file, 'r')
                # Version 7.3 mat files are not supported by sio.loadmat
                # if there is a 7.3 mat file, this try except will catch it
                # these files can be opened by h5py, as they are hdf5 data files.
		var_list = []
		for k in data.keys():
			if k[0] != '#':
				var_list.append(k)

	return var_list

def data_to_dict(hdf5_data):

	if type(hdf5_data) == hio._hl.group.Group or type(hdf5_data) == hio._hl.files.File:
		data_out = {}
		key_list = hdf5_data.keys()
		for key in key_list:
			data_out[key] = data_to_dict(hdf5_data[key])
	elif type(hdf5_data) == hio._hl.dataset.Dataset:		
		if hdf5_data.dtype.type == object_:				 
			data_out = cell_to_list(hdf5_data)
		else:			
			if 'MATLAB_int_decode' in hdf5_data.attrs.keys():
						data_out = string(hdf5_data.value)
			else:
				data_out = hdf5_data.value
	else:
		raise TypeError('data_to_dict expects a HDF5 data type input')

	return data_out

def cell_to_list(hdf5_data, data_file = None):

	if data_file == None:
		data_file = hdf5_data.file
		reshape_data = True
	else:
		reshape_data = False

	hdf5_shape = hdf5_data.shape
	data_out = []
	if len(hdf5_shape) > 1:
		for k in range(hdf5_shape[len(hdf5_shape)-2]):
			data_out.append(cell_to_list(hdf5_data[k], data_file))
	else:
		for k in range(hdf5_shape[0]):
			if type(data_file[hdf5_data[k]]) == hio._hl.dataset.Dataset:
				if len(data_file[hdf5_data[k]].shape) > 1:
					if 'MATLAB_int_decode' in data_file[hdf5_data[k]].attrs.keys():
						data_out.append(string(data_file[hdf5_data[k]].value))
					else:
						data_out.append(data_file[hdf5_data[k]].value)
				else:
					data_out.append([]) # matlab variables are always at least 2D, unless they are empty
			elif type(data_file[hdf5_data[k]]) == hio._hl.group.Group:
				data_out.append(data_to_dict(data_file[hdf5_data[k]]))

	if reshape_data:
		if prod(hdf5_shape) == prod(shape(data_out)):
			data_out = reshape(data_out, hdf5_shape)
	return data_out

if __name__ == "__main__":

	# This is here for testing purposes only
	return 0


HDF Compass Test Plan
=====================

The test plan includes Testing environment, Installation, Basic
functionality, Basic viewer tests, Plug-in tests, and a table to carry
out a test with a sample file.

kyang2014 write comments starting with kyang2014:

kyang2014: From the ticket and JR's
comments(https://github.com/HDFGroup/hdf-compass/issues/71) , it seems
this is just for the release validation. The tester doesn't need to
build HDFCompass from the source. The developer will provide the
binaries to the tester.

I. Testing environment

1) Platforms

+----------------+----------------------------------+
| **Platform**   | **Versions**                     |
+================+==================================+
| Mac OS         | MacOS 10.8, 10.9, 10.10, 10.11   |
+----------------+----------------------------------+
| Windows        | 7,8 and 10                       |
+----------------+----------------------------------+
| Linux          | 64-bit CentOS 6 and 7?           |
+----------------+----------------------------------+

kyang2014: Do we need the Python,h5py etc. versions? Seems that we don't need
these information just for this purpose?

2) Where to obtain the testing files

kyang2014: May use Amazon S3 or google cloud or azure.
I put some testing files for a quick test under
ftp://ftp.hdfgroup.uiuc.edu/pub/outgoing/HDFCompass/kent-files/


II. Installation

+----------------+-------------------------------------------+
| **Platform**   | **Experience**                            |
+================+===========================================+
| Mac OS         | ?                                         |
+----------------+-------------------------------------------+
| Windows        | Download and follow the instructions      |
+----------------+-------------------------------------------+
| Linux          | may need to install python dependencies   |
+----------------+-------------------------------------------+

 

III. Basic functionality

1) Launch HDFCompass

Click HDFCompass icon or type HDFCompass.exe under the command-line to
see if the program can get started.

2) Menu Tests

+-----------------+------------------------+----------------------------------+
| **File Menu**   | **File Menu Hotkey**   | **About HDFCompass**             |
+=================+========================+==================================+
| Open            | Ctrl- O                | HDFCompass Version number(0.5)   |
|                 |                        |                                  |
|                 |                        | @2014-2015 The HDF Group         |
+-----------------+------------------------+----------------------------------+
| Open Resource   | Ctrl-R                 |                                  |
+-----------------+------------------------+----------------------------------+
| Close Window    | Ctrl-W                 |                                  |
+-----------------+------------------------+----------------------------------+
| Close File      | Shift-Ctrl-W           |                                  |
+-----------------+------------------------+----------------------------------+
| Exit            |                        |                                  |
+-----------------+------------------------+----------------------------------+

3) Toolbar Icon displays (On mac). Can drag files to Toolbar?  

IV. Basic viewer Tests

1) Basic Tests

A)

+--------------------+--------------------------------------------------------------------+-----------------------------------------+----------------------------+--------------------------------+--------------------------------------+
| **Platform**       | **HDF5 Group**                                                     | **HDF5 Group Attributes**               | **HDF5 Dataset**           | **HDF5 Dataset Plots**         | **HDF5 Dataset Attributes**          |
+====================+====================================================================+=========================================+============================+================================+======================================+
| (items to check)   | 1. Tree view or List view                                          | 1. Click  "Reopen as HDF5 Attributes"   | name, shape,type, values   | Plot by clicking "Plot Data"   | Click  "Reopen as HDF5 Attributes"   |
|                    |                                                                    |                                         |                            |                                |                                      |
|                    | 2. Name and Kind                                                   | 2. name, values,type and shapes         |                            | Icons on the Plot windows      | name, value, type, values            |
|                    |                                                                    |                                         |                            |                                |                                      |
|                    | 3. Click "Reopen as HDF5 Group"  to check if it is still working   |                                         |                            |                                |                                      |
+--------------------+--------------------------------------------------------------------+-----------------------------------------+----------------------------+--------------------------------+--------------------------------------+
| Windows 7          |                                                                    |                                         |                            |                                |                                      |
+--------------------+--------------------------------------------------------------------+-----------------------------------------+----------------------------+--------------------------------+--------------------------------------+
| Linux CentOS 6     |                                                                    |                                         |                            |                                |                                      |
+--------------------+--------------------------------------------------------------------+-----------------------------------------+----------------------------+--------------------------------+--------------------------------------+
| MacOS 10.10        |                                                                    |                                         |                            |                                |                                      |
+--------------------+--------------------------------------------------------------------+-----------------------------------------+----------------------------+--------------------------------+--------------------------------------+
| .......            |                                                                    |                                         |                            |                                |                                      |
+--------------------+--------------------------------------------------------------------+-----------------------------------------+----------------------------+--------------------------------+--------------------------------------+

B)

On each window, check the "Go" icon

2) Advanced Tests

Same as the above but may need to provide the information that needs
specific attentions for some tests.

kyang2014: Do we want to test if one can open an HDF5 file >1 times at the
same time?

3) Files for the basic Tests

A) Really basic one:
A file that just includes one group, one HDF5
dataset of 2-D floating-point array, a string attribute under the group
and an integer attribute for the dataset.

B) Basic tests:

    a) Dataset: One group, one scalar, one 1-D array and one 3-D
    floating-point array.

    b) Group: multi-groups(no cycle)

    c) Attributes: Attributes of different types, from int8(signed and
    unsigned) to int64, floating-points, HDF5 string under a group

    d) Compound datatype datasets: a simple one and a nested one
    datasets as well as a simple and a nested attributes

 

C) Advanced tests:

    a) HDF5 object references: One dataset and one attribute

    b) HDF5 region references: One dataset and one attribute

    c) HDF5 softlink and hardlink: Links for groups and datasets

    d) HDF5 external links: Link to datasets and groups from another
    HDF5 file(Will this work?)

    e) HDF5 Image, table, packed table

    kyang2014: f) to i) should be more advanced.

    f) HDF5 datatypes(advanced):

    f1) HDF5 string: variable length string with different pad options,
    fixed-size string with different pad options

    f2) Big endian and Little endian mixed

    f3) Bitfield, enum, opaque and even array type

    g) HDF5 datasets(advanced)

    g1) HDF5 datasets applied to different filters and storage:
    gzip(different levels), shuffle, nbit, scaleoffset, szip, chunking,
    compact 

    g2) One 4-D and one 5-D array(Mainly for the plot feature)

    g3) Unlimited dimension HDF5 datasets : 1-D and 2-D

    h) HDF5 spaces(advanced)

    h1) Null space

    i) Stress tests:

    i1)Giant dataset > 4GB

    i2) Many attributes

    i3) Many objects

kyang2014: Need to get approved to implement the above testing plan. In the
mean time, I've just tried out the HDFCompass with some files I
collected by my own.

Issues I found are submitted to github issues 87-99.

My own testing files(included a few from JR) can be found under
ftp://ftp.hdfgroup.uiuc.edu/pub/outgoing/HDFCompass/kent-files/

V. Plug-in Tests

1) OPeNDAP

kyang2014:

*Needs the clarification about the purpose of OPeNDAP plug-in. DAP is a
protocol. Various formats such as netCDF, HDF4, HDF5, grib, excel etc.
can be accessed via DAP. Also there are different DAP implementations.
Different DAP implementations may provide different output. So we need
to clarify what implementation we should test.*

*Unidata's THREDDS(java) and OPeNDAP's Hyrax(C++) are two major ones. A
python implementation(pydap) is also available. *

*Also the OPeNDAP plug-in uses Pydap underneath to access the DAP data.
The Pydap client may also have its own limitation(See the last section
of kyang2014's comments for issue 60.

Since the HDF group implemented HDF modules for Hyrax, so first we
should target the HDF5 files served via Hyrax implementation of OPeNDAP.

A) Testing the access of HDF5 via Hyrax

Hyrax provides an option to dynamically enable different outputs. To
serve our NASA customers, we implement an option(CF option) in addition
to the default option for Hyrax output. In my view, default option is
more fit for HDFCompass although the CF option may be more practical for
users.Since the output is different for different options, we need to
provide the expected output for different options. 

The testing
files can be found under
ftp://ftp.hdfgroup.uiuc.edu/pub/outgoing/HDFCompass/kent-files/hdf5-handler-fake/

A1) Default option

a) DAP2 testing
This mapping keeps the original HDF5 structure via DAP2.

d_compound.h5
d_group.h5
d_objref.h5
d_regref.h5
d_link_soft.h5
d_link_hard.h5
d_int.h5
t_string.h5
t_vl_string.h5

b) DAP4 testing
Prerequiste: Pydap supports DAP4

d_compound.h5
d_group.h5
d_objref.h5
d_regref.h5
d_link_soft.h5
d_link_hard.h5
d_int.h5
d_int64.h5
t_string_cstr.h5
t_vl_string_cstr.h5
nc4_group_atomic.h5
nc4_group_comp.h5
 

A2) CF option

The output is more like netCDF output, which is like a subset of HDF5.
The variable/attribute names are following CF conventions. Groups are
flattened out. Bunch of datatypes not supported by CF are ignored. Some
customized features specifically requested from NASA are also added.
The DAP4 output is strictly mapped from the DAP2 output. So the testing files
are the same.

t_float.h5
t_group_scalar_attrs.h5
t_int.h5
t_2d_2dll.nc4.h5
t_cf_1dll.h5
t_size8.h5
t_string.h5
t_unsupported.h5
t_vl_string.h5
t_name_clash.h5
t_non_cf_char.h5
t_fillvalue_2d_2x2y.nc4.h5
grid_1_2d.h5


B) (Maybe) Testing the access of HDF4 via Hyrax

C) (Maybe) Testing the access of HDF5 via THREDDS

D) (Maybe) Testing the access of netCDF via THREDDS

.......

2) ASCII Grid

sample.asc can be found under the test directory.
kyang2014: Just have a check with the sample.asc of this plug-in. Actually I
don't think the plot is right although the data values in the viewer
looks like corresponding to the sample.asc.

The problem is the starting point of the plot index. HDFcompass
starting from the upper-left corner with index (0,0). The (0,0) in the ASCII
Grid should start from lower-left. So the plot is upside-down.This
example shows the compass contour plot feature is not sufficient. The
contour plot is not appropriate. The plot should be like the one at 
https://en.wikipedia.org/wiki/Esri_grid.

This Basic testing for this plug-in is relatively easy. It just needs
three tests.

1) Sample.asc

2) Sample.asc with xllcorner as 300.00 and yllcorner as 200.00

3) Sample.asc without having NODATA\_Value

VI. An example to check the functionality of the basic viewer

kyang2014: Fill in the information later if necessary

 

 

 

 

HDF Compass Test Plan
=====================

The test plan includes Testing environment, Installation, Basic
functionality, Basic viewer tests, Plug-in tests, and a table to carry
out a test with a sample file.

I  write comments starting with KY with the *italicized* font.

KY: *From the ticket and JR's
comments(https://github.com/HDFGroup/hdf-compass/issues/71) , it seems
this is just for the release validation. The tester doesn't need to
build HDFCompass from the source. The developer will provide the
binaries to the tester.*

**I. Testing environment**

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

KY: *Do we need the Python,h5py etc. versions? Seems that we don't need
these information just for this purpose.*

2) Where to obtain the testing files

KY:

*The quickest solution is to use the company's  ftp area:*
`*ftp://ftp.hdfgroup.uiuc.edu/pub/outgoing/* <ftp://ftp.hdfgroup.uiuc.edu/pub/outgoing/>`__

*An HDFCompass directory can be obtained and testing files can be put
there. S3 is also a good candidate. Any comments from other people?*

 

**II. Installation**

+----------------+-------------------------------------------+
| **Platform**   | **Experience**                            |
+================+===========================================+
| Mac OS         | ?                                         |
+----------------+-------------------------------------------+
| Windows        | Download and follow the instructions      |
+----------------+-------------------------------------------+
| Linux          | may need to install python dependencies   |
+----------------+-------------------------------------------+

 

**III. Basic functionality**

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

3) Toolbar Icon displays (On mac). Can drag files to Toolbar?  –(\ *KY: 
Not sure about this? Don't have a Mac machine to test this. Dragging
files to HDFCompass doesn't work on windows*)

**IV. Basic viewer Tests**

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

On each window, check the "Go" icon(\ *KY: currently the function
doesn't work on my windows 7 platform*)

2) Advanced Tests

Same as the above but may need to provide the information that needs
specific attention for some tests.

*KY: Do we want to test if one can open an HDF5 file >1 times at the
same time? *

3) Files for the basic Tests

A) Really basic one: A file that just includes one group, one HDF5
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

    *(KY: f to i should be more advanced)*

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

*KY: Need to get approved to implement the above testing plan. In the
mean time, I've just tried out the HDFCompass with some files I
collected by my own.*

*Issues I found are submitted to*
`*https://github.com/HDFGroup/hdf-compass/issues/* <https://github.com/HDFGroup/hdf-compass/issues/>`__
*with issue number 87-99. *

*My own testing files(included a few from JR) can be found under*
`*ftp://ftp.hdfgroup.uiuc.edu/pub/outgoing/HDFCompass/kent-files/* <ftp://ftp.hdfgroup.uiuc.edu/pub/outgoing/HDFCompass/kent-files/>`__

**V. Plug-in Tests**

1) OPeNDAP

KY: Fill in the information later if necessary (*From JR's email on
Oct.14,2015: Also it needs detail for OpenDAP testing and Asci Grid
plugin testing. So fill in some information now).*

*KY: *

*Needs the clarification about the purpose of OPeNDAP plug-in. DAP is a
protocol. Various formats such as netCDF, HDF4, HDF5, grib, excel etc.
can be accessed via DAP. Also there are different DAP implementations.
Different DAP implementations may provide different output. So we need
to clarify what implementation we should test.*

*Unidata's THREDDS(java) and OPeNDAP's Hyrax(C++) are two major ones. A
python implementation(pydap) is also available. *

*Also the OPeNDAP plug-in uses Pydap underneath to access the DAP data.
The Pydap client may also have its own limitation(See the last section
of kyang2014's comments at*
`*https://github.com/HDFGroup/hdf-compass/issues/60* <https://github.com/HDFGroup/hdf-compass/issues/60>`__\ *)*

Since the HDF group implemented HDF modules for Hyrax, so first we
should target the HDF5 files served via Hyrax implementation of OPeNDAP.

A) Testing the access of HDF5 via Hyrax

Hyrax provides an option to dynamically enable different outputs. To
serve our NASA customers, we implement an option(CF option) in addition
to the default option for Hyrax output. In my view, default option is
more fit for HDFCompass although the CF option may be more practical for
users.Since the output is different for different options, we need to
provide the **expected output **\ for different options. 

A1) Default option

This mapping keeps the original HDF5 structure via DAP2. The testing
files can be found under
https://svn.hdfgroup.uiuc.edu/hdf5_handler/trunk/data/ (eventually we
will provide a place just for OPeNDAP-plugin tests)

d\_compound.h5

d\_group.h5

| d\_objref.h5
| d\_regref.h5

d\_link\_soft.h5

d\_link\_hard.h5

| d\_int.h5
| t\_string.h5
| t\_vl\_string.h5

(If Pydap supports DAP4, following files should be added)

Check
https://svn.hdfgroup.uiuc.edu/hdf5_handler/trunk/bes-testsuite/hdf5_handlerTest.default.at

search dmr.bescmd and dap.bescmd for the corresponding files.

 

A2) CF option

The output is more like netCDF output, which is like a subset of HDF5.
The variable/attribute names are following CF conventions. Groups are
flattened out. Bunch of datatypes not supported by CF are ignored. Some
customized features specifically requested from NASA are also added.
*The testing files can be found under*

`*https://svn.hdfgroup.uiuc.edu/hdf5\_handler/trunk/data/* <https://svn.hdfgroup.uiuc.edu/hdf5_handler/trunk/data/>`__
*(eventually we will provide a place just for OPeNDAP-plugin tests)*

`*https://svn.hdfgroup.uiuc.edu/hdf5\_handler/trunk/bes-testsuite/hdf5\_handlerTest.cf.at* <https://svn.hdfgroup.uiuc.edu/hdf5_handler/trunk/bes-testsuite/hdf5_handlerTest.cf.at>`__
*can be used as a reference.*

t\_float.h5

t\_group\_scalar\_attrs.h5

t\_int.h5

| t\_2d\_2dll.nc4.h5
| t\_cf\_1dll.h5
| t\_size8.h5
| t\_string.h5
| t\_unsupported.h5
| t\_vl\_string.h5
| t\_name\_clash.h5
| t\_non\_cf\_char.h5
| t\_fillvalue\_2d\_2x2y.nc4.h5
| grid\_1\_2d.h5

 

*B) (Maybe) Testing the access of HDF4 via Hyrax*

*C) (Maybe) Testing the access of HDF5 via THREDDS*

*D) (Maybe) Testing the access of netCDF via THREDDS*

*.......*

2) ASCII Grid

(From JR: just keep a note for future work

This is information about the Ascii Grid
format: \ https://en.wikipedia.org/wiki/Esri_grid.  Ted's intern wrote a
plugin for it last summer as a starter project.  Attached is a `small
file <file:///C:\Users\ymuqun\Downloads\attach_a04f04baf1e496baed88678dff17dfbc>`__\ in
that format (if you can find some other's in that format, that will be
great).

*KY: Just have a check with the sample.asc of this plug-in. Actually I
don't think the plot is right although the data values in the viewer
looks like corresponding to the sample.asc. *

*The problem is the startin*\ g point of the plot index. HDFcompass
starting from the upper-left corner with index (0,0). The (0,0) ASCII
Grid should start from lower-left. So the plot is upside-down.This
example shows the compass contour plot feature is not sufficient. The
contour plot is not appropriate. The plot should be like the one at 
https://en.wikipedia.org/wiki/Esri\_grid.

This Basic testing for this plug-in is relatively easy. It just needs
three tests.

1) Sample.asc

2) Sample.asc with xllcorner as 300.00 and yllcorner as 200.00

3) Sample.asc without having NODATA\_Value

**VI. An example to check the functionality of the basic viewer**

*KY new: Not sure about this but keep the original note.*

*KY: Need to provide the expected output*

*Fill in the information later if necessary,*

 

 

 

 

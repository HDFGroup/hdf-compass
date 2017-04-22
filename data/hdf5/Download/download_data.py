"""
Download additional data files from AWS
"""

import os.path
try:
    import wget

except ImportError as e:
    print("missing wget, try to install it: pip install wget: %s" % e)
    import sys

    sys.exit(1)

files = [
    'ami_hdf.h5',
    'attrfile.h5',
    'craterlake.h5',
    'compound.h5',
    'comp_complex.h5',
    'countries.h5',
    'hapmap_compressed.h5',
    'hdf5_test.h5',
    'iso++.h5',
    'sequences.h5',
    'snps1000_chr22_CEU.h5',
    'LD_22_5Kx5K_matrix.h5',  # 5 MB
    'shuttle_hdf.h5',  # 8 MB
    'full8_400um.mnc.h5',  # 10MB
    'DOQ.h5',  # 45 MB
    'Sample_Urban_Data.h5',  # 145 MB
    'h5pf_md_manygroupnew2.h5',  # 155 MB
    'gz6_SCRIS_npp_d20140522_t0754579_e0802557_b13293__noaa_pop.h5',  # 187 MB
    # 'NARA_TWR.h5',  # 3 GB!  Uncomment if you really want this.
]

for filename in files:
    uri = 'https://s3.amazonaws.com/hdfgroup/data/hdf5test/' + filename
    print( uri)
    if os.path.isfile(filename):
        print(filename, "already downloaded - skipping")
    else:
        wget.download(uri, bar=wget.bar_thermometer)
print("done!")

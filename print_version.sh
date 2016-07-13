#!/bin/bash
FILE=setup.py
echo $FILE: `grep "setup_args\['version'\] =" $FILE`
FILE=docs/conf.py
echo $FILE: `grep "release = '" $FILE`
FILE=hdf_compass/utils/__init__.py
echo $FILE: `grep "__version__ =" $FILE`
FILE=setup.cfg
echo $FILE: `grep "current_version =" $FILE`
FILE=HDFCompass.1file.spec
echo $FILE: `grep "version =" $FILE`
FILE=HDFCompass.1folder.spec
echo $FILE: `grep "version =" $FILE` 
 

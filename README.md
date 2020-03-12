# CCB
This repo contains a set of general functions for performing everyday ccb'ing

Maintained by [Christopher Anderson](mailto:cbanders@stanford.edu) and [Jeff Smith](mailto:jrsmith7@stanford.edu)

### building the singularity container
Build the ccb singularity container using the `ccb-singularity.build` script.

```
# clone the latest version of the repo
git clone https://github.com/stanford-ccb/ccb.git
cd ccb/

# add the path to this repo as an environment variable
export CCB=$PWD
echo 'export CCB=$PWD' >> ~/.bashrc

# then build the singularity container into the bin directory
sudo singularity build bin/ccb ccb-singularity.build

# and add ccb/bin to your local path so you can easily access the container
export PATH=$CCB/bin:$PATH
echo 'export PATH=$CCB/bin:$PATH' >> ~/.bashrc
```

You can add then access the binary commands though the singularity container by typing e.g. `ccb gbif-to-vector -h`. You could also access the python module through e.g. `ccb ipython` then `import ccb`.


### Installation without singularity container

(1) Install java sdk from 
https://www.oracle.com/java/technologies/javase-downloads.html


Next steps have to be done from the ccb directory (the directory where this readme is located):

(2) Create a conda environment
```buildoutcfg 
$ conda env create -f environment.yml
```

(3) Download the maxent binary

May need on mac:
`$ brew install wget`

```buildoutcfg
$ wget https://biodiversityinformatics.amnh.org/open_source/maxent/maxent.php?op=download -O maxent.zip

$ unzip maxent.zip

$ rm maxent.bat maxent.zip
```

(4) Install this package in the conda env
```buildoutcfg 
$ conda activate ccb_env

$ pip install -e .
```

At this point you should be ready to run tests:
```python
$ pytest tests/
```




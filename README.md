# HPCCM containers

This repository contains a set python scripts that build containers (mostly in singularity) from Nvidia's [HPC Container Makers (HPCCM)](https://github.com/NVIDIA/hpc-container-maker)

Note that only the default arguments are tested. And those recipe with suffix `.wip` are not tested.

## Requirements

```
wget
flit
fire
```

## Installation

```
flit install
```
## Update recipes

```
cd src/hpccm_containers
./update-recipe.sh
```

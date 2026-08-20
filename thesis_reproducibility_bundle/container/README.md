# Apptainer image

The experiments require the same software environment used on the cluster.
The current image is:

- cluster path: `/home/hersco/Docker/image.sif`
- size: `646,361,088` bytes (about 617 MiB)

The image is included in this repository through Git LFS. After cloning, run:

```bash
git lfs install
git lfs pull
cd thesis_reproducibility_bundle/container
sha256sum -c image.sif.sha256
```

The compressed evaluation logs are also stored with Git LFS. A normal clone
with Git LFS installed downloads both the image and those logs. If LFS objects
were initially skipped, `git lfs pull` retrieves them later.

As an independent fallback, the image can be copied directly from the BGU
cluster and checked against the same digest:

```bash
scp hersco@slurm.bgu.ac.il:/home/hersco/Docker/image.sif ./image.sif
sha256sum -c image.sif.sha256
```

Example use:

```bash
apptainer exec \
  --bind "$PWD:$PWD" \
  --pwd "$PWD/asnets" \
  ./image.sif \
  /bin/bash
```

Do not substitute a different image without recording its digest and software
changes; TensorFlow, Java/JPDDL, ENHSP, and native planner dependencies affect
both execution and reproducibility.

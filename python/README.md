# Python Dockerfiles

## Run Jupyter from container

- `docker pull continuumio/miniconda`
- `docker run -i -t -p 8888:8888 continuumio/miniconda /bin/bash -c "/opt/conda/bin/conda install jupyterlab -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyterlab --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser"`

## Want more?

Check my other repos.

## References

- https://testdriven.io/blog/docker-best-practices/
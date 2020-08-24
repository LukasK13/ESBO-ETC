# Derive docker image from debian base image
FROM debian

# update package cache and isntall python 3 as well as pip 3
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Install the module necessary for virtual environments
RUN pip3 install virtualenv

# Use bash as entry point for the container
CMD ["/bin/bash"]
# Use the official Odoo 18 image as the base image.
FROM odoo:18

# Git branch of the module repository to clone.
# This can be overridden during build:
# docker build --build-arg MODULE_BRANCH=develop .
ARG MODULE_BRANCH=main

# Fixed GitHub repository containing the custom Odoo module.
ENV MODULE_REPO=https://github.com/trevor-gituru/odoo-meter-reading-module.git

# Switch to the root user so we can install packages and copy files.
USER root

# Install Git (required to clone the module repository) and
# clean the apt cache to keep the image size small.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Clone only the latest commit of the selected branch into
# Odoo's extra addons directory.
RUN git clone \
    --depth 1 \
    --branch ${MODULE_BRANCH} \
    ${MODULE_REPO} \
    /mnt/extra-addons/meter_invoice

# Copy the custom entrypoint script that generates odoo.conf
# from runtime environment variables before starting Odoo.
COPY docker/entrypoint.sh /entrypoint.sh

# Make the entrypoint executable.
RUN chmod +x /entrypoint.sh

# Run the custom entrypoint when the container starts.
ENTRYPOINT ["/entrypoint.sh"]

# Start Odoo. The entrypoint appends the generated configuration.
CMD ["odoo"]

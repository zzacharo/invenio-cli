# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio CLI Docker Compose class."""

import io
import logging
import os
import re
import subprocess
import tarfile

import docker

from .log import LogPipe

DOCKER_COMPOSE_VERSION_DASH = '1.21.0'


class DockerHelper(object):
    """Utility class to interact with docker-compose."""

    def __init__(self, log_config, local=True):
        """Constructor for the DockerCompose helper."""
        super(DockerHelper, self).__init__()
        self.local = local
        self.log_config = log_config
        self.docker_client = docker.from_env()
        # Set as INFO to allow all logs to be sent
        logging.basicConfig(filename=self.log_config.logfile,
                            level=logging.INFO)

    def build_image(self, dockerfile, tag):
        """Build docker image."""
        self.docker_client.images.build(path=os.getcwd(),
                                        dockerfile=dockerfile, tag=tag)

    def create_images(self):
        """Create images according to the specified environment."""
        # Open logging pipe
        logpipe = LogPipe(self.log_config)

        command = ['docker-compose',
                   '--file', 'docker-compose.full.yml', 'up', '--no-start']
        if self.local:
            command[2] = 'docker-compose.yml'

        subprocess.call(command, stdout=logpipe, stderr=logpipe)
        # Close logging pipe
        logpipe.close()

    def start_containers(self):
        """Start containers according to the specified environment."""
        command = ['docker-compose',
                   '--file', 'docker-compose.full.yml', 'up', '--no-recreate']

        if self.local:
            command[2] = 'docker-compose.yml'

        if not self.log_config.verbose:
            # Open logging pipe
            logpipe = LogPipe(self.log_config)

            command.append('-d')
            subprocess.call(command, stdout=logpipe, stderr=logpipe)

            # Close logging pipe
            logpipe.close()
        else:
            # TEST: Is this piping all logs of containers along with server's?
            subprocess.Popen(command,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def stop_containers(self):
        """Stop currently running containers."""
        command = ['docker-compose',
                   '--file', 'docker-compose.full.yml', 'stop']

        if self.local:
            command[2] = 'docker-compose.yml'

        # Open logging pipe
        logpipe = LogPipe(self.log_config)

        subprocess.call(command, stdout=logpipe, stderr=logpipe)

        # Close logging pipe
        logpipe.close()

    def destroy_containers(self):
        """Stop and remove all containers, volumes and images."""
        # Open logging pipe
        logpipe = LogPipe(self.log_config)

        command = ['docker-compose', '--file', 'docker-compose.full.yml',
                   'down', '--volumes']
        if self.local:
            command[2] = 'docker-compose.yml'

        subprocess.call(command, stdout=logpipe, stderr=logpipe)

        # Close logging pipe
        logpipe.close()

    def _normalize_name(self, project_shortname):
        """Normalize the container name according to the compose version.

        Docker-Compose introduced support for dash and underscore in
        version 1.21.0.
        """
        dc_version_command = subprocess.Popen(['docker-compose', '--version'],
                                              stdout=subprocess.PIPE)

        dc_version_string = dc_version_command.communicate()[0]
        dc_version_string = dc_version_string.decode("utf-8").strip()

        groups = re.search(r'1.[0-9]*.[0-9]*', dc_version_string)
        dc_version = groups.group(0)

        if dc_version < DOCKER_COMPOSE_VERSION_DASH:
            return re.sub(r'[^a-z0-9]', '', project_shortname)
        else:
            return project_shortname

    def copy(self, src_file, dst_path, project_shortname):
        """Copy a file into the path of the specified container."""
        container_name = '{}_web-ui_1'.format(
            self._normalize_name(project_shortname))
        container = self.docker_client.containers.get(container_name)

        with tarfile.open('tmp.tar', "w") as tar:
            tar.add(src_file, arcname=os.path.basename(src_file),
                    recursive=False)
        with open('tmp.tar', 'rb') as fin:
            data = io.BytesIO(fin.read())
            container.put_archive(dst_path, data)

    def execute_cli_command(self, project_shortname, command):
        """Execute an invenio CLI command in the API container."""
        container_name = '{}_web-api_1'.format(
            self._normalize_name(project_shortname))
        container = self.docker_client.containers.get(container_name)

        status = container.exec_run(
            cmd='/bin/bash -c "{}"'.format(command.replace('"', '\\"')),
            user='invenio',
            tty=True,
            stdout=True,
            stderr=True)

        if self.log_config.verbose:
            print(status.output.decode("utf-8"))
        else:
            level = logging.INFO if status.exit_code == 0 else logging.ERROR
            logging.log(level, status.output.decode("utf-8").strip('\n'))

        return status.exit_code

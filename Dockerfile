# Pull base image from AWS ECR Public

ARG FUNCTION_DIR="/src"
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}

# Set environment variables
ENV IS_DOCKER_HOST 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Libraries and build dependencies (required for cryptography and any libs requiring a compiler)
RUN apt-get -qq update && apt-get -y upgrade && apt-get install --reinstall build-essential -y \
  && \
  apt install netcat-traditional \
  && \
  apt-get -y install \
  git \
  && \
  apt-get clean && \
  apt-get install openssh-client -y && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installing dependency package - python
RUN pip install --upgrade pip  \
        aws-encryption-sdk-cli \
        awscli pipenv
# Copied requirements
COPY Pipfile Pipfile.lock ${FUNCTION_DIR}/

# Install any needed packages specified in pip file
ENV GIT_SSH_COMMAND="ssh -i /docker-deployments.key -o UserKnownHostsFile=/known_hosts"
COPY docker-deployments.key* /
RUN chmod 0600 /docker-deployments.key  || true
RUN ssh-keyscan bitbucket.org > /known_hosts
RUN pipenv install --system --deploy --ignore-pipfile
RUN rm /docker-deployments.key  || true


# Copy Project
ADD ./src ${FUNCTION_DIR}

# exposing port
EXPOSE 9000

# Run the application, change the command as needed for your application.
# Please ensure that the command is added to the 'run_server.py' script to execute when the container is launched.

CMD ["python","run_server.py"]

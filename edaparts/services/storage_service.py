#
# MIT License
#
# Copyright (c) 2020 Pablo Rodriguez Nava, @pablintino
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#


import base64
import logging
import os
import subprocess
import git

from edaparts.app.config import Config
from edaparts.models.internal.internal_models import StorageStatus
from edaparts.services.exceptions import FileNotFoundStorageError, InvalidStorageStateError
from edaparts.utils.helpers import BraceMessage as __l

__logger = logging.getLogger(__name__)


def __get_ssh_command():
    git_ssh_cmd = '/usr/bin/ssh -i %s' % Config.SSH_IDENTITY if ((Config.SSH_IDENTITY is not None)
                                                                 and os.path.isfile(Config.SSH_IDENTITY)) \
        else '/usr/bin/ssh'
    git_ssh_cmd = f'{git_ssh_cmd} -o "StrictHostKeyChecking=no"' if ((Config.SSH_HOSTS_FILE is None)
                                                                     or not os.path.isfile(Config.SSH_HOSTS_FILE)) else \
        f'{git_ssh_cmd} -o "UserKnownHostsFile={Config.SSH_HOSTS_FILE}"'
    return git_ssh_cmd


def __is_git_repo():
    return subprocess.call(["git", "branch"], cwd=Config.REPO_PATH, stderr=subprocess.STDOUT,
                           stdout=open(os.devnull, 'w')) == 0


def __get_repo(git_ssh_cmd):
    # If repo already exists just get it
    if __is_git_repo():
        repo = git.Repo(Config.REPO_PATH)
    else:
        # If repo doesn't exist just clone it using the URL environment variable
        if Config.REPO_URL is None:
            raise IOError('REPO_PATH point to a non initialized repository and REPO_URL was not given')

        repo = git.Repo.clone_from(Config.REPO_URL, Config.REPO_PATH, branch=Config.REPO_BRANCH,
                                   env=dict(GIT_SSH_COMMAND=git_ssh_cmd))

    return repo


def create_file_in_repo(repo, file_name, encoded_data):
    file_content = base64.b64decode(encoded_data)
    abs_file_path = os.path.join(repo.working_dir, file_name)
    os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)
    with open(abs_file_path, 'wb') as f:
        f.write(file_content)


def add_file_to_repo(file_name, encoded_data):
    git_ssh_cmd = __get_ssh_command()
    __logger.debug(f'Using git ssh command {git_ssh_cmd}')
    repo = __get_repo(git_ssh_cmd)
    with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        repo.remotes.origin.fetch()
        repo.remotes.origin.pull()

        # Check if file already exists
        is_update = os.path.exists(file_name)

        create_file_in_repo(repo, file_name, encoded_data)
        repo.git.add(file_name)
        repo.index.commit('Auto commit to ' + ('add ' if not is_update else 'update ') + file_name)
        repo.remotes.origin.push(force=True)
        __logger.debug(__l('File stored successfully [file_name={0}]'))


def get_file_from_repo(model):
    if model.get_storage_status() != StorageStatus.STORED:
        raise InvalidStorageStateError('Model is not in STORED state', entity_id=model.id,
                                       current_state=model.get_storage_status().name)
    file_name = model.get_file_path()
    abs_file_path = os.path.join(Config.REPO_PATH, file_name)
    if not os.path.isfile(abs_file_path):
        msg = f'{file_name} does not exist'
        __logger.debug(msg)
        raise FileNotFoundStorageError(msg)

    return abs_file_path


def get_encoded_file_from_repo(model):
    abs_file_path = get_file_from_repo(model)
    with open(abs_file_path, "rb") as file:
        return base64.b64encode(file.read())

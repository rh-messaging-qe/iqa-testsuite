#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
#

"""
Utility class to help executing OpenShift standard operations
"""
from iqa_common.executor import Executor, Execution, Command


# TODO Merge PR #3 on iqa-common which contains this new class (and remove it from iqa-testsuite)
class OpenShiftUtil(object):
    """
    Helper class that helps executing standard operations through the "oc" cli.
    """

    TIMEOUT = 30

    def __init__(self, executor: Executor, url: str, token: str):
        self.executor = executor
        self.url = url
        self.token = token

    def login_first(func):
        def wrap(*args, **kwargs):
            instance = args[0]
            assert instance.login().completed_successfully()
            return func(*args, **kwargs)
        return wrap

    def login(self, timeout=TIMEOUT) -> Execution:
        cmd_login = Command(args=['oc', 'login', self.url, '--token="%s"' % self.token],
                            timeout=timeout, stderr=True, stdout=True)
        execution: Execution = self.executor.execute(cmd_login)
        execution.wait()
        return execution

    @login_first
    def scale(self, replicas: int, deployment: str) -> Execution:
        cmd_scale_up = Command(args=['oc', 'scale', '--replicas=%d' % replicas, 'dc', deployment],
                               timeout=30, stderr=True, stdout=True)
        execution: Execution = self.executor.execute(cmd_scale_up)
        execution.wait()
        return execution

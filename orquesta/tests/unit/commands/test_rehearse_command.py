# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import mock
import six
import unittest

from orquesta.commands import rehearsal
from orquesta import exceptions as exc
from orquesta.tests.fixtures import loader as fixture_loader


class WorkflowRehearsalSpecTest(unittest.TestCase):
    @mock.patch.object(
        argparse.ArgumentParser,
        "parse_args",
        mock.MagicMock(
            return_value=argparse.Namespace(
                base_path="/path/does/not/exist",
                test_spec="tests/sequential_success.yaml",
                debug=False,
            )
        ),
    )
    def test_rehearse_bad_base_path(self):
        assertRaisesRegex = self.assertRaisesRegex if six.PY3 else self.assertRaisesRegexp

        assertRaisesRegex(
            exc.WorkflowRehearsalError,
            'The base path "/path/does/not/exist" does not exist.',
            rehearsal.rehearse,
        )

    @mock.patch.object(
        argparse.ArgumentParser,
        "parse_args",
        mock.MagicMock(
            return_value=argparse.Namespace(
                base_path=fixture_loader.get_rehearsal_fixtures_base_path(),
                test_spec="tests/foobar.yaml",
                debug=False,
            )
        ),
    )
    def test_rehearse_bad_test_spec(self):
        test_spec_path = "%s/tests/foobar.yaml" % fixture_loader.get_rehearsal_fixtures_base_path()

        assertRaisesRegex = self.assertRaisesRegex if six.PY3 else self.assertRaisesRegexp

        assertRaisesRegex(
            exc.WorkflowRehearsalError,
            'The test spec "%s" does not exist.' % test_spec_path,
            rehearsal.rehearse,
        )

    @mock.patch.object(
        argparse.ArgumentParser,
        "parse_args",
        mock.MagicMock(
            return_value=argparse.Namespace(
                base_path=fixture_loader.get_rehearsal_fixtures_base_path(),
                test_spec="tests/sequential_success.yaml",
                debug=False,
            )
        ),
    )
    def test_rehearse_success(self):
        rehearsal.rehearse()

    @mock.patch.object(
        argparse.ArgumentParser,
        "parse_args",
        mock.MagicMock(
            return_value=argparse.Namespace(
                base_path=fixture_loader.get_rehearsal_fixtures_base_path(),
                test_spec="tests/sequential_failure.yaml",
                debug=False,
            )
        ),
    )
    def test_rehearse_failure(self):
        assertRaisesRegex = self.assertRaisesRegex if six.PY3 else self.assertRaisesRegexp

        assertRaisesRegex(
            AssertionError,
            "The lists of task execution sequence do not match.",
            rehearsal.rehearse,
        )

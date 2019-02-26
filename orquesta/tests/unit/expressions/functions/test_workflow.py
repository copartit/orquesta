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

import copy
import unittest

from orquesta import constants
from orquesta import exceptions as exc
from orquesta.expressions.functions import workflow as funcs
from orquesta import states


class WorkflowFunctionTest(unittest.TestCase):

    def test_task_state_empty_context(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        context = None
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

        context = {}
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

        context = {'__flow': None}
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

        context = {'__flow': {}}
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

        context = {'__flow': {'tasks': None}}
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

        context = {'__flow': {'tasks': {}}}
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

        task_pointers = {task_flow_pointer_id: None}
        context = {'__flow': {'tasks': task_pointers}}
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

        task_pointers = {task_flow_pointer_id: 0}
        context = {'__flow': {'tasks': task_pointers, 'sequence': [None]}}
        self.assertEqual(funcs.task_state_(context, task_name, task_route), states.UNSET)

    def test_task_state_empty_context_with_no_given_route(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))
        task_pointers = {task_flow_pointer_id: None}

        context = None
        self.assertEqual(funcs.task_state_(context, task_name), states.UNSET)

        context = {}
        self.assertEqual(funcs.task_state_(context, task_name), states.UNSET)

        context_test_cases = [
            {'__flow': None},
            {'__flow': {}},
            {'__flow': {'tasks': None}},
            {'__flow': {'tasks': task_pointers}},
            {'__flow': {'tasks': task_pointers, 'sequence': [None]}}
        ]

        for context in context_test_cases:
            self.assertRaises(
                exc.ExpressionEvaluationException,
                funcs.task_state_,
                context,
                task_name
            )

    def test_task_state_empty_context_with_no_given_route_but_current_task_set(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))
        task_pointers = {task_flow_pointer_id: None}

        context_test_cases = [
            {},
            {'__flow': None},
            {'__flow': {}},
            {'__flow': {'tasks': None}},
            {'__flow': {'tasks': task_pointers}},
            {'__flow': {'tasks': task_pointers, 'sequence': [None]}}
        ]

        for context in context_test_cases:
            context['__current_task'] = {'id': task_name, 'route': task_route}
            self.assertEqual(funcs.task_state_(context, task_name), states.UNSET)

    def test_task_state_dereference_errors(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        task_pointers = {task_flow_pointer_id: 0}
        context = {'__flow': {'tasks': task_pointers}}
        self.assertRaises(IndexError, funcs.task_state_, context, task_name, task_route)

        task_pointers = {task_flow_pointer_id: 1}
        context = {'__flow': {'tasks': task_pointers, 'sequence': [{'state': states.RUNNING}]}}
        self.assertRaises(IndexError, funcs.task_state_, context, task_name, task_route)

    def test_task_state(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        task_pointers = {task_flow_pointer_id: 0}
        context = {'__flow': {'tasks': task_pointers, 'sequence': [{'state': states.RUNNING}]}}
        actual_task_state = funcs.task_state_(context, task_name, route=task_route)
        self.assertEqual(actual_task_state, states.RUNNING)

    def test_task_state_route_from_current_task(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        task_pointers = {task_flow_pointer_id: 0}
        context = {
            '__current_task': {'id': task_name, 'route': task_route},
            '__flow': {
                'tasks': task_pointers,
                'sequence': [{'state': states.RUNNING}]}
        }

        actual_task_state = funcs.task_state_(context, task_name)
        self.assertEqual(actual_task_state, states.RUNNING)

    def test_get_current_task_empty(self):
        self.assertRaises(exc.ExpressionEvaluationException, funcs._get_current_task, None)

        context = {'__current_task': None}
        self.assertRaises(exc.ExpressionEvaluationException, funcs._get_current_task, context)

        context = {'__current_task': {}}
        self.assertRaises(exc.ExpressionEvaluationException, funcs._get_current_task, context)

    def test_get_current_task(self):
        context = {'__current_task': {'id': 't1', 'route': 0}}
        self.assertDictEqual(funcs._get_current_task(context), context['__current_task'])

    def test_succeeded(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        context = {'__current_task': None}
        self.assertRaises(exc.ExpressionEvaluationException, funcs.succeeded_, context)

        context = {
            '__current_task': {'id': task_name, 'route': task_route},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.RUNNING}]
            }
        }

        self.assertFalse(funcs.succeeded_(context))

        context = {
            '__current_task': {'id': task_name, 'route': task_route},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.SUCCEEDED}]
            }
        }

        self.assertTrue(funcs.succeeded_(context))

    def test_failed(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        context = {'__current_task': None}
        self.assertRaises(exc.ExpressionEvaluationException, funcs.failed_, context)

        context = {
            '__current_task': {'id': task_name, 'route': task_route},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.RUNNING}]
            }
        }

        self.assertFalse(funcs.failed_(context))

        context = {
            '__current_task': {'id': task_name, 'route': task_route},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.FAILED}]
            }
        }

        self.assertTrue(funcs.failed_(context))

    def test_completed(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        context = {'__current_task': None}
        self.assertRaises(exc.ExpressionEvaluationException, funcs.completed_, context)

        context = {
            '__current_task': {'id': task_name, 'route': task_route},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.RUNNING}]
            }
        }

        self.assertFalse(funcs.completed_(context))

        context = {
            '__current_task': {'id': task_name, 'route': task_route},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.SUCCEEDED}]
            }
        }

        self.assertTrue(funcs.completed_(context))

    def test_result(self):
        task_route = 0
        task_name = 't1'
        task_flow_pointer_id = constants.TASK_FLOW_ROUTE_FORMAT % (task_name, str(task_route))

        context = {'__current_task': None}
        self.assertRaises(exc.ExpressionEvaluationException, funcs.result_, context)

        context = {
            '__current_task': {'id': task_name, 'route': task_route, 'result': 'foobar'},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.SUCCEEDED}]
            }
        }

        self.assertEqual(funcs.result_(context), 'foobar')

        context = {
            '__current_task': {'id': task_name, 'route': task_route, 'result': {'fu': 'bar'}},
            '__flow': {
                'tasks': {task_flow_pointer_id: 0},
                'sequence': [{'state': states.SUCCEEDED}]
            }
        }

        self.assertDictEqual(funcs.result_(context), {'fu': 'bar'})

    def test_task_state_of_tasks_along_split(self):
        task_pointers = {
            't1__r0': 0,
            't2__r0': 1,
            't3__r0': 2,
            't4__r1': 3,
            't4__r2': 4,
            't5__r1': 5,
            't5__r2': 6,
            't6__r1': 7,
            't6__r2': 8
        }

        task_flow_entries = [
            {'id': 't1', 'route': 0, 'state': states.SUCCEEDED},
            {'id': 't2', 'route': 0, 'state': states.SUCCEEDED},
            {'id': 't3', 'route': 0, 'state': states.SUCCEEDED},
            {'id': 't4', 'route': 1, 'state': states.SUCCEEDED},
            {'id': 't4', 'route': 2, 'state': states.FAILED},
            {'id': 't5', 'route': 1, 'state': states.SUCCEEDED},
            {'id': 't5', 'route': 2, 'state': states.FAILED},
            {'id': 't6', 'route': 1, 'state': states.SUCCEEDED},
            {'id': 't6', 'route': 2, 'state': states.FAILED},
        ]

        routes = [
            [],
            ['t2__t0'],
            ['t3__t0'],
        ]

        context = {
            '__flow': {
                'tasks': task_pointers,
                'sequence': task_flow_entries,
                'routes': routes
            }
        }

        # Check the task states along route 1.
        current_ctx = copy.deepcopy(context)
        current_ctx['__current_task'] = {'id': 't6', 'route': 1}
        self.assertEqual(funcs.task_state_(current_ctx, 't1'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't2'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't3'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't4'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't5'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't6'), states.SUCCEEDED)

        # Check the task states along route 2.
        current_ctx = copy.deepcopy(context)
        current_ctx['__current_task'] = {'id': 't6', 'route': 2}
        self.assertEqual(funcs.task_state_(current_ctx, 't1'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't2'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't3'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't4'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't5'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't6'), states.FAILED)

    def test_task_state_of_tasks_along_splits(self):
        task_pointers = {
            't1__r0': 0,
            't2__r0': 1,
            't3__r0': 2,
            't4__r1': 3,
            't4__r2': 4,
            't5__r1': 5,
            't5__r2': 6,
            't6__r1': 7,
            't6__r2': 8,
            't7__r3': 9,
            't7__r4': 10,
            't7__r5': 11,
            't7__r6': 12
        }

        task_flow_entries = [
            {'id': 't1', 'route': 0, 'state': states.SUCCEEDED},
            {'id': 't2', 'route': 0, 'state': states.SUCCEEDED},
            {'id': 't3', 'route': 0, 'state': states.SUCCEEDED},
            {'id': 't4', 'route': 1, 'state': states.SUCCEEDED},
            {'id': 't4', 'route': 2, 'state': states.FAILED},
            {'id': 't5', 'route': 1, 'state': states.SUCCEEDED},
            {'id': 't5', 'route': 2, 'state': states.FAILED},
            {'id': 't6', 'route': 1, 'state': states.SUCCEEDED},
            {'id': 't6', 'route': 2, 'state': states.FAILED},
            {'id': 't7', 'route': 3, 'state': states.SUCCEEDED},
            {'id': 't7', 'route': 4, 'state': states.FAILED},
            {'id': 't7', 'route': 5, 'state': states.RUNNING},
            {'id': 't7', 'route': 6, 'state': states.DELAYED}
        ]

        routes = [
            [],
            ['t2__t0'],
            ['t3__t0'],
            ['t2__t0', 't5__t0'],
            ['t3__t0', 't5__t0'],
            ['t2__t0', 't6__t0'],
            ['t3__t0', 't6__t0']
        ]

        context = {
            '__flow': {
                'tasks': task_pointers,
                'sequence': task_flow_entries,
                'routes': routes
            }
        }

        # Check the task states along route 1.
        current_ctx = copy.deepcopy(context)
        current_ctx['__current_task'] = {'id': 't7', 'route': 3}
        self.assertEqual(funcs.task_state_(current_ctx, 't1'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't2'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't3'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't4'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't5'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't6'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't7'), states.SUCCEEDED)

        # Check the task states along route 2.
        current_ctx = copy.deepcopy(context)
        current_ctx['__current_task'] = {'id': 't7', 'route': 4}
        self.assertEqual(funcs.task_state_(current_ctx, 't1'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't2'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't3'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't4'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't5'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't6'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't7'), states.FAILED)

        # Check the task states along route 3.
        current_ctx = copy.deepcopy(context)
        current_ctx['__current_task'] = {'id': 't7', 'route': 5}
        self.assertEqual(funcs.task_state_(current_ctx, 't1'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't2'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't3'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't4'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't5'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't6'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't7'), states.RUNNING)

        # Check the task states along route 4.
        current_ctx = copy.deepcopy(context)
        current_ctx['__current_task'] = {'id': 't7', 'route': 6}
        self.assertEqual(funcs.task_state_(current_ctx, 't1'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't2'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't3'), states.SUCCEEDED)
        self.assertEqual(funcs.task_state_(current_ctx, 't4'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't5'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't6'), states.FAILED)
        self.assertEqual(funcs.task_state_(current_ctx, 't7'), states.DELAYED)

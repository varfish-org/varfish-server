"""Django commands that make debugging celery tasks easier.

For example, execute the command as follows.

  $ python manage.py runtask myproject.tasks.example_task --task-args '[1, 2, 3]'

Executing the above command will perform the same processing as the following code.

  >>> from myproject.tasks import example_task
  >>> example_task(1, 2, 3)

Use `--pdb` to stop while running.

  $ python manage.py runtask myproject.tasks.example_task --task-args '[1, 2, 3]' --pdb


LICENSE

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "TakesxiSximada"

import importlib
import inspect
import json
import pdb

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Django commands that make debugging celery tasks easier"

    def add_arguments(self, parser):
        parser.add_argument("dottedname", help="The dotted name of the callable object.")
        parser.add_argument(
            "--task-args",
            default="[]",
            type=json.loads,
            help="Arguments passed to the task. (default: '[]')",
        )
        parser.add_argument(
            "--task-kwargs",
            default="{}",
            type=json.loads,
            help="Keyword arguments passed to the task. (default: '{}')",
        )
        parser.add_argument("--pdb", action="store_true", help="Stop execution by debugger.")
        parser.add_argument(
            "--pdb-offset",
            default=0,
            type=int,
            help="Offset for debugger to create breakpoint. (default: 0)",
        )

    def handle(self, **options):
        dotted_list = options["dottedname"].strip().split(".")
        module_name = ".".join(dotted_list[:-1])
        func_name = dotted_list[-1]

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            self.stderr.write(f"No module: {module_name}")
            return

        try:
            func = getattr(module, func_name)
        except AttributeError:
            self.stderr.write(f"No attribute: {func_name} not in {module_name}")
            return

        if not callable(func):
            self.stderr.write(f"Not function: {module_name}.{func_name}")
            return

        if options["pdb"]:
            lineno = inspect.getsourcelines(func)[1] + options["pdb_offset"]
            debugger = pdb.Pdb()
            debugger.set_break(module.__file__, lineno=lineno, funcname=func_name)
            debugger.set_trace()

        result = func(*options["task_args"], **options["task_kwargs"])
        self.stdout.write(f"Return: {json.dumps(result)}")

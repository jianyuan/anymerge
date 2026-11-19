import subprocess
import sys
import textwrap

import pytest

MERGE_DATACLASS = """
import dataclasses, operator, sys, typing
import anymerge

@dataclasses.dataclass
class Model:
    a: typing.Annotated[int, anymerge.Reducer(operator.add)] = 0

assert anymerge.merge(Model(a=1), {"a": 2}) == Model(a=3)
"""


@pytest.mark.parametrize(
    ("setup", "check"),
    [
        pytest.param("", "assert 'pydantic' not in sys.modules", id="not-imported"),
        # Setting the module to None makes `import pydantic` fail, as if it weren't installed
        pytest.param("import sys; sys.modules['pydantic'] = None", "", id="not-installed"),
    ],
)
def test_works_without_pydantic(setup: str, check: str):
    code = textwrap.dedent(setup) + MERGE_DATACLASS + check
    subprocess.run([sys.executable, "-c", code], check=True)  # noqa: S603 - code is a constant from this file

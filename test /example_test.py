
import pytest

def add(num1, num2):
    return num1+num2

@pytest.mark.parametrize("num1, num2, expected", [
    (2, 3, 5),
    (4,4,8)
])
def test_add(num1, num2, expected):
    assert add(num1,num2) == expected
    
# to run: pytest -v or look at learningPoints.odt in /snakey/basicApi
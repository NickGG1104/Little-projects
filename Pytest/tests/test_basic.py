import pytest
from src.basic import *
from fixture import test_lst


# # # # # # # # # # # # # # # # # # # # # # # #
#                  Calculate                  #
# # # # # # # # # # # # # # # # # # # # # # # #
# Ver. 1
def test_add():
    assert add(2, 3) == 5


# Ver. 2
@pytest.mark.parametrize('a,b,expect', [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 3, 2),
    (-1, 3, 2)
])
def test_add_param(a, b, expect):
    assert add(a, b) == expect


# # # # # # # # # # # # # # # # # # # # # # # #
#                   String                    #
# # # # # # # # # # # # # # # # # # # # # # # #
# Ver. 1
def test_concat():
    str_1 = 'Hello! '
    str_2 = 'World!'
    assert concat(str_1=str_1, str_2=str_2) == 'Hello! World!'


# Ver. 2
def test_concat_failed():
    str_1 = 555
    str_2 = 666
    with pytest.raises(TypeError):  # 以下範圍內的程式碼應該要拋出 Type Error
        concat(str_1=str_1, str_2=str_2)


# Ver. 3
def test_concat_fixture(test_lst):
    assert concat(str_1=test_lst[0], str_2=test_lst[1]) == 'Hello! World!', '輸入字串錯誤！'

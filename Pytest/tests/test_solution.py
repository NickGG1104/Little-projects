import pytest
from src.leetcode_solutions import Solution


@pytest.mark.parametrize('nums,target,expect', [
    ([2, 7, 11, 15], 9, [0, 1]),
    ([3, 2, 4], 6, [1, 2]),
    ([3, 3], 6, [0, 1]),
])
def test_two_sum(nums, target, expect):
    assert Solution().twoSum(nums, target) == expect


def test_no_answer_returns_empty():
    assert Solution().twoSum([1, 2, 3], 100) == []

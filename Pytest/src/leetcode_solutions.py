# # # # # # # # # # # # # # # # # # # # # # # #
#                  LeetCode                   #
# # # # # # # # # # # # # # # # # # # # # # # #
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen: dict[int, int] = {}
        for i, x in enumerate(nums):
            y = target - x
            if y in seen:              # 先找 y 避免同一索引被用兩次
                return [seen[y], i]
            seen[x] = i                # 最後再記錄目前值的位置
        return []

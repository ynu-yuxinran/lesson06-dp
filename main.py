# -*- coding: utf-8 -*-
# =============================================================
# 《人工智能程序设计与实践》课程作业 —— 动态规划专题（第6次作业）
# 实验一：硬币找零（贪心法 vs 动态规划法）
# 实验二：0-1背包问题（二维dp表格 + 回溯求组合）
# 拓展一：预算800g对比实验
# 拓展二：必投项目（强制必须选择睡袋）
# 运行环境：Python 3.x，仅使用Python标准库，无第三方包
# 运行方式：在命令行执行  python main.py
# =============================================================

INF = float('inf')  # 哨兵值：表示“该金额暂时无法凑出”（无穷大）

# ==================== 实验一：硬币找零 ====================

def coin_greedy(coins, amount):
    """贪心法求硬币找零：每一轮都优先使用当前能用的最大面额。
    返回 (硬币总数量, 硬币组合列表)；若无法凑出返回 (None, [])。"""
    coins = sorted(coins, reverse=True)   # 面额从大到小排列
    used = []                             # 记录用掉的每一枚硬币
    remain = amount                       # 还剩多少钱没有凑
    for c in coins:
        while remain >= c:                # 只要装得下当前最大面额，就一直用它
            used.append(c)
            remain -= c
    if remain != 0:                       # 循环结束仍有剩余 → 凑不出
        return None, []
    return len(used), used

def coin_dp(coins, amount):
    """动态规划求最少硬币数（完全背包思想：每种面额可用无限次）。
    dp[a]    ：凑出金额 a 所需的最少硬币数
    record[a]：凑出金额 a 时“最后一枚”使用的面额，专门用于回溯组合
    返回 (最少硬币数, 硬币组合列表)。"""
    dp = [INF] * (amount + 1)
    dp[0] = 0                             # 边界条件：凑0元需要0枚硬币
    record = [0] * (amount + 1)           # 题目要求的 record 路径记录数组
    for a in range(1, amount + 1):        # 自底向上：从小金额算到大金额
        for c in coins:                   # 枚举“最后一枚”硬币的面额 c
            if c <= a and dp[a - c] + 1 < dp[a]:
                # ★核心递推（硬币版）：dp[a] = min( dp[a-c] + 1 )，对每个面额c
                dp[a] = dp[a - c] + 1     # 由子问题 a-c 再加一枚面额 c 得到 a
                record[a] = c             # 记下这一步使用的面额，供回溯使用
    if dp[amount] == INF:                 # 该金额无法凑出
        return None, []
    used = []                             # ---- 回溯 record 数组还原硬币组合 ----
    a = amount
    while a > 0:
        used.append(record[a])            # 取出凑出金额a时用的最后一枚硬币
        a -= record[a]                    # 金额回退，继续向前回溯
    return dp[amount], used

# ============ 实验二：0-1背包（二维dp表格 + 回溯选物） ============

def knapsack_01(items, capacity):
    """标准0-1背包：二维dp表格 + 回溯求选中物品组合。
    严格采用课本递推公式：dp[i][c] = max(dp[i-1][c], dp[i-1][c-w] + v)
    采用“至多装满”变体：dp整表初始化为0，不要求恰好装满背包。
    参数 items: [(名称, 重量g, 价值), ...]；返回 (最大价值, 选中物品列表, dp表)"""
    n = len(items)
    # dp[i][c]：只考虑前 i 件物品、背包容量为 c 时能获得的最大总价值
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):             # 逐个引入第 i 件物品
        name, w, v = items[i - 1]         # 取出第i件物品的名称、重量、价值
        for c in range(capacity + 1):     # 枚举背包容量 c
            if c >= w:
                # ★★★ 核心递推公式（课本原式），课堂指认下一行代码 ★★★
                # dp[i][c] = max( 不选第i件: dp[i-1][c] , 选第i件: dp[i-1][c-w]+v )
                dp[i][c] = max(dp[i - 1][c], dp[i - 1][c - w] + v)
            else:
                dp[i][c] = dp[i - 1][c]   # 容量装不下 → 第i件只能不选
    # ---------- 回溯dp表格，反推被选中的物品 ----------
    chosen = []
    c = capacity
    for i in range(n, 0, -1):             # 从最后一件物品向前回溯
        if dp[i][c] != dp[i - 1][c]:      # 选与不选价值不同 → 说明第i件被选中
            chosen.append(items[i - 1][0])
            c -= items[i - 1][1]          # 扣除该物品占用的容量
    chosen.reverse()                      # 回溯是倒着走的，反转为正常顺序
    return dp[n][capacity], chosen, dp

def knapsack_forced(items, capacity, must_name):
    """拓展二：必投项目——强制必须选中指定物品（本作业指定睡袋）。
    思路：先“预支”睡袋占用的重量与带来的价值，剩余容量交给其余四件物品
    做标准0-1背包，最后把睡袋的价值加回、名称放到组合最前面。"""
    must = None
    for it in items:                      # 第一步：找到必投物品
        if it[0] == must_name:
            must = it
            break
    rest = [it for it in items if it[0] != must_name]   # 第二步：其余四件物品
    rest_value, rest_chosen, _ = knapsack_01(rest, capacity - must[1])
    return rest_value + must[2], [must[0]] + rest_chosen

# ==================== 辅助打印函数 ====================

def format_coins(used):
    """把 [5, 5, 5] 这样的硬币列表整理成 '5元×3枚' 的可读格式"""
    counter = {}
    for c in used:
        counter[c] = counter.get(c, 0) + 1
    parts = ["{}元×{}枚".format(k, counter[k]) for k in sorted(counter, reverse=True)]
    return " + ".join(parts)

def print_result(items, value, chosen):
    """统一打印背包实验结果：最大价值、选中物品及物品总重量"""
    weight_of = {name: w for name, w, v in items}
    total_w = sum(weight_of[name] for name in chosen)
    print("  最大总价值 = {}".format(value))
    print("  选中物品   = {}".format("、".join(chosen) if chosen else "（无）"))
    print("  物品总重量 = {}g".format(total_w))

# ==================== 主程序：依次运行全部实验 ====================

if __name__ == "__main__":
    # ---------- 实验一：硬币找零 ----------
    print("=" * 60)
    print("实验一：硬币找零（面额[1, 5, 11]，目标金额15）")
    print("=" * 60)
    coins = [1, 5, 11]
    amount = 15

    g_count, g_used = coin_greedy(coins, amount)
    print("[贪心法]   硬币数量 = {}，组合 = {}".format(g_count, format_coins(g_used)))
    d_count, d_used = coin_dp(coins, amount)
    print("[动态规划]  硬币数量 = {}，组合 = {}".format(d_count, format_coins(d_used)))
    print(">> 对比结论：贪心先拿11元陷入局部最优(共5枚)；动态规划得全局最优(共3枚)。")

    # ---------- 实验二：0-1背包（限重1000g） ----------
    print()
    print("=" * 60)
    print("实验二：0-1背包动态规划（背包限重1000g，“至多装满”变体）")
    print("=" * 60)
    items = [
        ("帐篷", 300, 60),   # (名称, 重量g, 重要度/价值)
        ("炉具", 200, 80),
        ("睡袋", 350, 90),
        ("食物", 400, 130),
        ("水具", 250, 95),
    ]
    v1, chosen1, dp1 = knapsack_01(items, 1000)
    print_result(items, v1, chosen1)
    print(">> 预期校验：最大总价值应为315，选中 睡袋、食物、水具（合计恰好1000g）。")

    # ---------- 拓展一：预算800g对比实验 ----------
    print()
    print("=" * 60)
    print("拓展一：预算800g对比实验")
    print("=" * 60)
    v2, chosen2, dp2 = knapsack_01(items, 800)
    print_result(items, v2, chosen2)
    print(">> 对比结论：容量降到800g后，睡袋+食物+水具(需1000g)装不下了，")
    print("   最优解变为 炉具+睡袋+水具(恰好800g)，总价值由315降至{}。".format(v2))

    # ---------- 拓展二：必投项目（强制选睡袋） ----------
    print()
    print("=" * 60)
    print("拓展二：必投项目（强制必须选择睡袋，背包容量1000g）")
    print("=" * 60)
    v3, chosen3 = knapsack_forced(items, 1000, "睡袋")
    print_result(items, v3, chosen3)
    print(">> 说明：睡袋(350g/90分)必选，剩余650g容量中最优搭配为 食物+水具(650g/225分)。")
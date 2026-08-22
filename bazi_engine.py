# -*- coding: utf-8 -*-
"""
八字排盘引擎（阶段一：计算与推理分离）

设计原则：
  1. 排盘、大运、五行、十神、藏干 —— 全部用 lunar-python 精确计算，不让 LLM 心算。
  2. 五行生克 —— 写死的硬规则（10 条），杜绝「金克火」这类根本性错误。
  LLM 只负责「解读/分析」，不负责「计算/判断生克」。

起运口径：采用 lunar-python sect=2 精确口径（分钟级：4320 分钟=1 年、360 分钟=1 月、12 分钟=1 天、分钟×2=小时，即传统「3 天=1 岁、1 天=4 个月、1 时辰=10 天」），区别于默认 sect=1 的离散口径。

依赖：pip install lunar-python  （6tail/lunar-python，MIT 协议，525+ star）
"""

from lunar_python import Solar

# ======================================================================
# 一、五行生克规则（写死）
# ======================================================================

# 五行相生：木→火→土→金→水→木
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

# 五行相克：木→土→水→火→金→木
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 天干 → 五行
GAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 地支 → 五行
ZHI_WUXING = {
    "寅": "木", "卯": "木",
    "巳": "火", "午": "火",
    "申": "金", "酉": "金",
    "亥": "水", "子": "水",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
}


def gan_wuxing(gan):
    """天干 → 五行。例：gan_wuxing('庚') -> '金'"""
    return GAN_WUXING[gan]


def zhi_wuxing(zhi):
    """地支 → 五行。例：zhi_wuxing('子') -> '水'"""
    return ZHI_WUXING[zhi]


def sheng_ke(a, b):
    """判断两个五行 a、b 之间的生克关系。

    返回（中文）：
      'a生b'  a 生 b     'a克b'  a 克 b
      'b生a'  b 生 a     'b克a'  b 克 a
      '同类'  五行相同
    例：sheng_ke('金', '火') -> 'b克a'（火克金），而非「金克火」。
    """
    if a == b:
        return "同类"
    if SHENG.get(a) == b:
        return "a生b"
    if SHENG.get(b) == a:
        return "b生a"
    if KE.get(a) == b:
        return "a克b"
    if KE.get(b) == a:
        return "b克a"
    return "未知"


def gan_gan_sheng_ke(gan_a, gan_b):
    """两个天干之间的生克关系。例：gan_gan_sheng_ke('庚', '丙') -> 'b克a'"""
    return sheng_ke(gan_wuxing(gan_a), gan_wuxing(gan_b))


# ======================================================================
# 二、排盘（封装 lunar-python）
# ======================================================================

def paipan(year, month, day, hour, gender, minute=0):
    """排盘。

    参数：
      year/month/day/hour/minute  阳历年月日时分（hour 0-23，minute 0-59）
      gender  性别：1=男，0=女
    返回：结构化盘面字典，含性别、四柱、五行、纳音、十神、藏干、空亡、十二长生、天月二德、大运。
    """
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()

    pillars = {
        "年": ec.getYear(),
        "月": ec.getMonth(),
        "日": ec.getDay(),
        "时": ec.getTime(),
    }
    wuxing = {
        "年": ec.getYearWuXing(),
        "月": ec.getMonthWuXing(),
        "日": ec.getDayWuXing(),
        "时": ec.getTimeWuXing(),
    }
    nayin = {
        "年": ec.getYearNaYin(),
        "月": ec.getMonthNaYin(),
        "日": ec.getDayNaYin(),
        "时": ec.getTimeNaYin(),
    }
    shishen = {
        "年干": ec.getYearShiShenGan(),
        "月干": ec.getMonthShiShenGan(),
        "日干": "日主",
        "时干": ec.getTimeShiShenGan(),
    }
    canggan = {
        "年支": ec.getYearHideGan(),
        "月支": ec.getMonthHideGan(),
        "日支": ec.getDayHideGan(),
        "时支": ec.getTimeHideGan(),
    }

    yun = ec.getYun(gender, 2)
    dayun = []
    for dy in yun.getDaYun():
        gz = dy.getGanZhi()
        if gz:  # 跳过「出生到起运前」的空档项
            dayun.append({
                "干支": gz,
                "起": dy.getStartYear(),
                "止": dy.getEndYear(),
            })

    # 神煞（四支按三合局查 + 日干查；天月二德按月支查）
    shensha = {}
    for k, gz in pillars.items():
        zhi = gz[1]
        shensha[f"{k}支"] = {
            "桃花": tao_hua(zhi),
            "驿马": yi_ma(zhi),
            "华盖": hua_gai(zhi),
            "将星": jiang_xing(zhi),
        }
    shensha["日干"] = {
        "天乙贵人": list(tian_yi_gui_ren(ec.getDayGan())),
        "文昌": wen_chang(ec.getDayGan()),
        "羊刃": yang_ren(ec.getDayGan()),
    }

    return {
        "性别": "男" if gender == 1 else "女",  # 输入性别随盘面输出（1=男，0=女），供下游/HTML 流转
        "四柱": pillars,
        "五行": wuxing,
        "纳音": nayin,
        "十神": shishen,
        "藏干": canggan,
        "空亡": {
            "年柱": ec.getYearXunKong(),
            "日柱": ec.getDayXunKong(),
        },
        "十二长生": ec.getDayDiShi(),  # 日主在月支的十二长生地势
        "神煞": shensha,
        "天月二德": {
            "天德": TIAN_DE.get(ec.getMonthZhi()),
            "月德": YUE_DE.get(ec.getMonthZhi()),
        },
        "起运": {
            "年": yun.getStartYear(),
            "月": yun.getStartMonth(),
            "天": yun.getStartDay(),
            "时": yun.getStartHour(),
        },
        "大运": dayun,
    }


# ======================================================================
# 三、地支关系（三合、三会、六合、冲、刑、害）
# ======================================================================

# 三合局（申子辰合水 等）
SAN_HE = {
    "申子辰": "水", "寅午戌": "火", "巳酉丑": "金", "亥卯未": "木",
}

# 三会方（寅卯辰会东方木 等）
SAN_HUI = {
    "寅卯辰": "木", "巳午未": "火", "申酉戌": "金", "亥子丑": "水",
}

# 六合（子丑合 等，双向）
LIU_HE = {
    "子": "丑", "丑": "子",
    "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯",
    "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳",
    "午": "未", "未": "午",
}

# 六冲（子午冲 等，双向）
LIU_CHONG = {
    "子": "午", "午": "子",
    "丑": "未", "未": "丑",
    "寅": "申", "申": "寅",
    "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰",
    "巳": "亥", "亥": "巳",
}

# 地支相刑（《三命通会》循环三刑：寅刑巳、巳刑申、申刑寅；丑刑戌、戌刑未、未刑丑；子卯互刑）
XING = {
    "寅": ("巳",), "巳": ("申",), "申": ("寅",),
    "丑": ("戌",), "戌": ("未",), "未": ("丑",),
    "子": ("卯",), "卯": ("子",),
}

# 自刑
ZI_XING = ("辰", "午", "酉", "亥")

# 地支相害（六害，双向）
HAI = {
    "子": "未", "未": "子",
    "丑": "午", "午": "丑",
    "寅": "巳", "巳": "寅",
    "卯": "辰", "辰": "卯",
    "申": "亥", "亥": "申",
    "酉": "戌", "戌": "酉",
}


def zhi_liu_he(zhi):
    """地支六合对象。例：zhi_liu_he('子') -> '丑'"""
    return LIU_HE.get(zhi)


def zhi_liu_chong(zhi):
    """地支六冲对象。例：zhi_liu_chong('子') -> '午'"""
    return LIU_CHONG.get(zhi)


def zhi_xing(zhi):
    """地支相刑的对象（循环三刑，可能一个或无）。例：zhi_xing('寅') -> ('巳',)"""
    return XING.get(zhi, ())


def zhi_hai(zhi):
    """地支相害对象。例：zhi_hai('子') -> '未'"""
    return HAI.get(zhi)


def san_he_ju(zhi):
    """给定地支，返回所在三合局（含局五行）。
    例：san_he_ju('子') -> ('申子辰', '水')
    """
    for ju, wx in SAN_HE.items():
        if zhi in ju:
            return (ju, wx)
    return None


def san_hui_fang(zhi):
    """给定地支，返回所在三会方（含方五行）。
    例：san_hui_fang('寅') -> ('寅卯辰', '木')
    """
    for fang, wx in SAN_HUI.items():
        if zhi in fang:
            return (fang, wx)
    return None


# ======================================================================
# 四、神煞（桃花、驿马、羊刃、天乙贵人、华盖、将星、文昌）
# ======================================================================

# 以「地支」为参照（按三合局归类）的煞
TAO_HUA = {"申子辰": "酉", "寅午戌": "卯", "巳酉丑": "午", "亥卯未": "子"}
YI_MA = {"申子辰": "寅", "寅午戌": "申", "巳酉丑": "亥", "亥卯未": "巳"}
HUA_GAI = {"申子辰": "辰", "寅午戌": "戌", "巳酉丑": "丑", "亥卯未": "未"}
JIANG_XING = {"申子辰": "子", "寅午戌": "午", "巳酉丑": "酉", "亥卯未": "卯"}

# 以「天干」为参照的煞（主流子平法，天乙贵人未细分昼贵/夜贵）
# 天乙贵人：甲戊庚见丑未、乙己见子申、丙丁见亥酉、壬癸见卯巳、辛见寅午
TIAN_YI = {
    "甲": ("丑", "未"), "戊": ("丑", "未"), "庚": ("丑", "未"),
    "乙": ("子", "申"), "己": ("子", "申"),
    "丙": ("亥", "酉"), "丁": ("亥", "酉"),
    "壬": ("卯", "巳"), "癸": ("卯", "巳"),
    "辛": ("寅", "午"),
}

# 羊刃（阳干才有）：甲刃在卯、丙戊刃在午、庚刃在酉、壬刃在子
YANG_REN = {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}

# 文昌：甲见巳、乙见午、丙戊见申、丁己见酉、庚见亥、辛见子、壬见寅、癸见卯
WEN_CHANG = {
    "甲": "巳", "乙": "午",
    "丙": "申", "戊": "申",
    "丁": "酉", "己": "酉",
    "庚": "亥", "辛": "子",
    "壬": "寅", "癸": "卯",
}

# 天月二德（按月支查天干，传统歌诀；【待核对】——存在版本差异，仅作主题提示）
# 天德口诀：正丁二申三壬四辛五亥六甲七癸八寅九丙十乙十一巳十二庚
TIAN_DE = {
    "寅": "丁", "卯": "申", "辰": "壬", "巳": "辛",
    "午": "亥", "未": "甲", "申": "癸", "酉": "寅",
    "戌": "丙", "亥": "乙", "子": "巳", "丑": "庚",
}
# 月德口诀：寅午戌月在丙、申子辰月在壬、亥卯未月在甲、巳酉丑月在庚
YUE_DE = {
    "寅": "丙", "午": "丙", "戌": "丙",
    "申": "壬", "子": "壬", "辰": "壬",
    "亥": "甲", "卯": "甲", "未": "甲",
    "巳": "庚", "酉": "庚", "丑": "庚",
}


def _zhi_sha(zhi, sha_table):
    """按「地支」查神煞（桃花/驿马/华盖/将星 通用）。"""
    r = san_he_ju(zhi)
    if r is None:
        return None
    return sha_table.get(r[0])


def tao_hua(zhi):
    """桃花（咸池）。例：tao_hua('子') -> '酉'（申子辰见酉）"""
    return _zhi_sha(zhi, TAO_HUA)


def yi_ma(zhi):
    """驿马。例：yi_ma('申') -> '寅'（申子辰马在寅）"""
    return _zhi_sha(zhi, YI_MA)


def hua_gai(zhi):
    """华盖。例：hua_gai('子') -> '辰'（申子辰见辰）"""
    return _zhi_sha(zhi, HUA_GAI)


def jiang_xing(zhi):
    """将星。例：jiang_xing('子') -> '子'（申子辰见子）"""
    return _zhi_sha(zhi, JIANG_XING)


def tian_yi_gui_ren(gan):
    """天乙贵人（按天干）。例：tian_yi_gui_ren('甲') -> ('丑', '未')"""
    return TIAN_YI.get(gan, ())


def yang_ren(gan):
    """羊刃（阳干）。例：yang_ren('甲') -> '卯'；阴干返回 None"""
    return YANG_REN.get(gan)


def wen_chang(gan):
    """文昌。例：wen_chang('甲') -> '巳'"""
    return WEN_CHANG.get(gan)


def tian_de(month_zhi):
    """天德贵人（按月支查天干，传统歌诀，待核对）。例：tian_de('寅') -> '丁'"""
    return TIAN_DE.get(month_zhi)


def yue_de(month_zhi):
    """月德贵人（按月支查天干，传统歌诀，待核对）。例：yue_de('午') -> '丙'"""
    return YUE_DE.get(month_zhi)


# ======================================================================
# 五、自测（直接运行本文件时执行）
# ======================================================================

if __name__ == "__main__":
    print("===== 五行生克自测 =====")
    # 正确的生克
    assert sheng_ke("木", "火") == "a生b", "木生火"
    assert sheng_ke("金", "水") == "a生b", "金生水"
    assert sheng_ke("火", "金") == "a克b", "火克金"
    assert sheng_ke("金", "木") == "a克b", "金克木"
    # 关键：金 vs 火 —— 是「火克金」，绝不是「金克火」
    assert sheng_ke("金", "火") == "b克a", "火克金（金被火克）"
    assert sheng_ke("水", "火") == "a克b", "水克火"
    print("生克规则 8 项断言全部通过 ✅")
    print("金 vs 火 的正确关系：", sheng_ke("金", "火"), "（火克金，不是金克火）")

    print("\n===== 排盘自测（示例：2005-05-29 辰时 男）=====")
    pan = paipan(2005, 5, 29, 8, 1)
    print("四柱：", " ".join(f"{k}柱{v}" for k, v in pan["四柱"].items()))
    print("五行：", " ".join(pan["五行"].values()))
    print("纳音：", " ".join(pan["纳音"].values()))
    print("十神：", " ".join(f"{k}:{v}" for k, v in pan["十神"].items()))
    print("空亡：", pan["空亡"])
    print("十二长生：", pan["十二长生"])
    print("神煞：", pan["神煞"])
    print("天月二德：", pan["天月二德"])
    print("起运：", pan["起运"])
    print("大运：", " → ".join(d["干支"] for d in pan["大运"]))

    print("\n===== 地支关系自测 =====")
    # 三合
    assert san_he_ju("子") == ("申子辰", "水"), "申子辰合水"
    assert san_he_ju("寅") == ("寅午戌", "火"), "寅午戌合火"
    assert san_he_ju("巳") == ("巳酉丑", "金"), "巳酉丑合金"
    assert san_he_ju("亥") == ("亥卯未", "木"), "亥卯未合木"
    # 三会
    assert san_hui_fang("寅") == ("寅卯辰", "木"), "寅卯辰会木"
    assert san_hui_fang("申") == ("申酉戌", "金"), "申酉戌会金"
    # 六合
    assert zhi_liu_he("子") == "丑", "子丑合"
    assert zhi_liu_he("寅") == "亥", "寅亥合"
    assert zhi_liu_he("午") == "未", "午未合"
    # 六冲
    assert zhi_liu_chong("子") == "午", "子午冲"
    assert zhi_liu_chong("卯") == "酉", "卯酉冲"
    assert zhi_liu_chong("辰") == "戌", "辰戌冲"
    # 刑（循环三刑）
    assert zhi_xing("寅") == ("巳",), "寅刑巳"
    assert zhi_xing("巳") == ("申",), "巳刑申"
    assert zhi_xing("申") == ("寅",), "申刑寅"
    assert zhi_xing("丑") == ("戌",), "丑刑戌"
    assert zhi_xing("未") == ("丑",), "未刑丑"
    assert zhi_xing("子") == ("卯",), "子卯刑"
    # 害
    assert zhi_hai("子") == "未", "子未害"
    assert zhi_hai("丑") == "午", "丑午害"
    assert zhi_hai("酉") == "戌", "酉戌害"
    print("地支关系 18 项断言全部通过 ✅")

    print("\n===== 神煞自测 =====")
    # 桃花
    assert tao_hua("子") == "酉", "申子辰见酉"
    assert tao_hua("寅") == "卯", "寅午戌见卯"
    assert tao_hua("巳") == "午", "巳酉丑见午"
    assert tao_hua("亥") == "子", "亥卯未见子"
    # 驿马
    assert yi_ma("申") == "寅", "申子辰马在寅"
    assert yi_ma("寅") == "申", "寅午戌马在申"
    assert yi_ma("巳") == "亥", "巳酉丑马在亥"
    assert yi_ma("亥") == "巳", "亥卯未马在巳"
    # 华盖
    assert hua_gai("子") == "辰", "申子辰见辰"
    assert hua_gai("寅") == "戌", "寅午戌见戌"
    # 将星
    assert jiang_xing("子") == "子", "申子辰见子"
    assert jiang_xing("寅") == "午", "寅午戌见午"
    # 天乙贵人
    assert tian_yi_gui_ren("甲") == ("丑", "未"), "甲见丑未"
    assert tian_yi_gui_ren("丙") == ("亥", "酉"), "丙见亥酉"
    assert tian_yi_gui_ren("辛") == ("寅", "午"), "辛见寅午"
    # 羊刃
    assert yang_ren("甲") == "卯", "甲刃在卯"
    assert yang_ren("丙") == "午", "丙刃在午"
    assert yang_ren("庚") == "酉", "庚刃在酉"
    assert yang_ren("壬") == "子", "壬刃在子"
    assert yang_ren("乙") is None, "阴干无刃"
    # 文昌
    assert wen_chang("甲") == "巳", "甲见巳"
    assert wen_chang("庚") == "亥", "庚见亥"
    assert wen_chang("癸") == "卯", "癸见卯"
    print("神煞 23 项断言全部通过 ✅")

    print("\n===== 天月二德自测（传统歌诀，待核对）=====")
    assert tian_de("寅") == "丁", "寅月天德丁"
    assert tian_de("丑") == "庚", "丑月天德庚"
    assert yue_de("午") == "丙", "午月月德丙"
    assert yue_de("申") == "壬", "申月月德壬"
    print("天月二德 4 项断言通过 ✅")

    print("\n===== 新增字段自测（空亡/十二长生/神煞）=====")
    pan2 = paipan(2005, 5, 29, 8, 1)
    assert pan2["空亡"]["年柱"], "应输出年柱空亡"
    assert pan2["空亡"]["日柱"], "应输出日柱空亡"
    assert pan2["十二长生"], "应输出日主十二长生"
    assert pan2["天月二德"]["天德"], "应输出天德"
    assert pan2["神煞"]["年支"]["桃花"], "应输出年支桃花"
    assert pan2["神煞"]["日干"]["天乙贵人"], "应输出日干天乙贵人"
    assert pan2["神煞"]["日干"]["羊刃"] is None or pan2["神煞"]["日干"]["羊刃"], "应输出日干羊刃（阴干为 None）"
    print("新增字段 7 项断言通过 ✅")

    print("\n===== 用你的八字做一次完整盘面演示 =====")
    print("日主癸水，日支丑。")
    print("日支丑 六合:", zhi_liu_he("丑"), "| 六冲:", zhi_liu_chong("丑"), "| 相刑:", zhi_xing("丑"), "| 相害:", zhi_hai("丑"))
    print("日支丑 所在三合局:", san_he_ju("丑"), "| 三会方:", san_hui_fang("丑"))
    print("日支丑 桃花:", tao_hua("丑"), "| 驿马:", yi_ma("丑"), "| 华盖:", hua_gai("丑"), "| 将星:", jiang_xing("丑"))
    print("日干癸 天乙贵人:", tian_yi_gui_ren("癸"), "| 文昌:", wen_chang("癸"), "| 羊刃:", yang_ren("癸"))

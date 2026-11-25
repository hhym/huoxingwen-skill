#!/usr/bin/env python3
"""火星文转换与还原（无第三方依赖）。

数据来源见 README 致谢：Niefee/textConversion（三表）、esbatmop/MNBVC（语料抽样）。

用法：
    python3 huoxingwen.py convert "我爱你" --level 2
    python3 huoxingwen.py restore "莪愛伱"
"""

import argparse
import random
import re
import sys
import unicodedata

from mars_dict import JT, FT, HX

# 正字 -> 火星文变体（单字符变体，保证可逆）
# 带 ★ 的条目来自 MNBVC 里屋论坛语料抽样（见 MNBVC-火星文资料/）
MAP = {
    "我": ["莪", "涐"],
    "你": ["伱", "妳"],
    "他": ["怹", "彵"],
    "她": ["祂"],
    "爱": ["愛", "噯"],
    "的": ["嘚", "の", "旳", "啲", "哋", "ぬ"],
    "是": ["係", "湜", "昰"],
    "不": ["卟", "鈈", "吥"],
    "很": ["狠", "佷"],
    "想": ["缃", "葙"],
    "会": ["會", "徻"],
    "说": ["說", "説"],
    "话": ["話", "諙"],
    "人": ["亾", "朲"],
    "心": ["吢", "鈊"],
    "天": ["兲", "添"],
    "日": ["ㄖ"],
    "月": ["仴", "岄"],
    "年": ["哖", "姩"],
    "时": ["溡", "時"],
    "间": ["間", "簡"],
    "在": ["茬", "恠"],
    "这": ["這"],
    "么": ["嬷", "麽", "仫"],
    "谁": ["誰", "夀"],
    "吗": ["嚤", "嘛"],
    "呢": ["哾"],
    "啊": ["錒", "呵"],
    "哦": ["喔", "筽"],
    "呀": ["吖", "丫"],
    "好": ["恏"],
    "坏": ["壊", "壞"],
    "欢": ["懽", "歡"],
    "快": ["筷", "赽"],
    "乐": ["泺", "樂"],
    "伤": ["慯", "傷"],
    "痛": ["痌"],
    "哭": ["唿"],
    "笑": ["笶"],
    "泪": ["涙", "淚"],
    "风": ["闏", "風"],
    "雪": ["鳕"],
    "云": ["蕓", "雲"],
    "星": ["暒"],
    "夜": ["亱"],
    "梦": ["夣", "夢"],
    "路": ["璐"],
    "远": ["逺", "遠"],
    "走": ["疋"],
    "来": ["徕", "來"],
    "去": ["厾", "呿"],
    "看": ["瞅"],
    "听": ["聴", "聽"],
    "读": ["牘", "讀"],
    "写": ["冩", "寫"],
    "字": ["牸", "茡"],
    "书": ["箸", "書"],
    "朋": ["倗"],
    "友": ["苃"],
    "家": ["傢", "宊"],
    "妈": ["嫲", "媽"],
    "哥": ["滒"],
    "姐": ["姊"],
    "弟": ["弚"],
    "妹": ["妺"],
    "子": ["孒", "仔", "孓"],
    "女": ["钕"],
    "男": ["侽"],
    "生": ["泩", "甥"],
    "个": ["個", "戈"],
    "们": ["門", "們"],
    "自": ["洎"],
    "知": ["倁"],
    "道": ["檤"],
    "觉": ["覺", "覅"],
    "得": ["淂"],
    "可": ["苛"],
    "以": ["苡"],
    "没": ["沒", "莈"],
    "有": ["冇", "洧"],
    "永": ["咏"],
    "守": ["垨"],
    "护": ["護"],
    "诺": ["諾"],
    "思": ["偲"],
    "念": ["唸"],
    "回": ["囬"],
    "忆": ["憶"],
    "青": ["圊"],
    "春": ["舂"],
    "寂": ["漃"],
    "孤": ["咕"],
    "单": ["單", "啴"],
    "忧": ["憂"],
    "幸": ["圉"],
    "福": ["鍢"],
    "微": ["薇"],
    "世": ["丗"],
    "界": ["堺"],
    "命": ["掵"],
    "情": ["啨"],
    "同": ["哃"],
    "学": ["學", "壆"],
    "师": ["師", "帥"],
    "真": ["眞"],
    "假": ["叚"],
    "美": ["媄"],
    "谢": ["謝"],
    "对": ["對", "対"],
    "起": ["杞"],
    "请": ["請"],
    "问": ["問"],
    "答": ["荅"],
    "今": ["仐"],
    "明": ["朙"],
    "过": ["過", "辻"],
    "现": ["哯"],
    "作": ["莋"],
    "事": ["亊"],
    "还": ["還"],
    "给": ["給"],
    "因": ["囙"],
    "为": ["為", "爲"],
    "比": ["仳"],
    "如": ["洳"],
    "果": ["菓"],
    "要": ["喓"],
    "到": ["菿", "箌"],
    "都": ["嘟"],
    "让": ["讓"],
    "开": ["開"],
    "关": ["関"],
    "见": ["見", "笕"],
    "头": ["頭"],
    "发": ["發"],
    "长": ["長"],
    "高": ["髙"],
    "大": ["夶"],
    "小": ["尛"],
    "少": ["仯"],
    "上": ["仩"],
    "下": ["丅"],
    "左": ["佐"],
    "右": ["佑"],
    "国": ["國", "囯"],
    "民": ["囻"],
    "后": ["後"],
    "前": ["偂"],
    "东": ["東"],
    "西": ["茜"],
    "南": ["喃"],
    "北": ["苝"],
    "黑": ["黒"],
    "红": ["紅"],
    "黄": ["黃"],
    "蓝": ["藍"],
    "绿": ["綠"],
    "最": ["蕞", "朂"],
    "近": ["菦"],
    "喜": ["囍"],
    "欢": ["懽"],
    "陪": ["蓜"],
    "伴": ["姅"],
    "等": ["踭"],
    "待": ["垈"],
    "承": ["乗"],
    "受": ["垨"],
    "疼": ["痋"],
    "抱": ["笣"],
    "歉": ["慊"],
    "原": ["厡"],
    "谅": ["諒"],
    "信": ["伩"],
    "任": ["紝"],
    "坚": ["堅"],
    "持": ["歭"],
    "努": ["劦"],
    "力": ["仂"],
    "奋": ["奮"],
    "斗": ["鬥"],
    "了": ["叻"],
    "老": ["咾"],
    "封": ["葑"],
    "壳": ["殼"],
    "手": ["掱"],
    "相": ["楿"],
    "容": ["嫆"],
    "易": ["噫"],
    "连": ["連"],
    "脑": ["脳"],
    "残": ["殘"],
    "鸭": ["鴨"],
    "再": ["侢"],
    "奖": ["獎"],
    "里": ["裏"],
    "样": ["樣"],
    "困": ["囷"],
}

# 变体 -> 正字
REV = {}
for _k, _vs in MAP.items():
    for _v in _vs:
        REV.setdefault(_v, _k)
REV.setdefault("┅", "一")  # 制表符 U+2505 被借作“一”

SYMBOLS = "☆★ゞ灬゛ゝゞ丶ヽヾミ彡〆メ﹏﹌﹋・…×·~〃※◎◇◆●○°•→"

CIRCLED = {str(i): ch for i, ch in enumerate("⓪①②③④⑤⑥⑦⑧⑨", start=0)}

# 常见谐音/符号（仅还原时参考，不展开）
NOTES = {
    "520": "我爱你",
    "1314": "一生一世",
    "886": "拜拜了",
}


_FULL_MAP = None
_FULL_REV = None


def _full_tables():
    """全量表：只收“既非原字、也非规范繁体”的汉字位映射。"""
    global _FULL_MAP, _FULL_REV
    if _FULL_MAP is None:
        m, r = {}, {}
        for a, b, f in zip(JT, HX, FT):
            if a == b or b == f or not ("\u4e00" <= a <= "\u9fff"):
                continue
            m.setdefault(a, [])
            if b not in m[a]:
                m[a].append(b)
            r.setdefault(b, a)  # 冲突时取索引靠前的简体
        _FULL_MAP, _FULL_REV = m, r
    return _FULL_MAP, _FULL_REV


def get_map(mode):
    return MAP if mode == "builtin" else _full_tables()[0]


def get_rev(mode):
    return REV if mode == "builtin" else _full_tables()[1]


def _variants(ch, level, rng, mapping):
    vs = mapping[ch]
    return vs[:1] if level == 1 else vs


def convert(text, level=2, seed=None, dict_mode="builtin"):
    rng = random.Random(seed if seed is not None else text)
    mapping = get_map(dict_mode)
    out = []
    last_sym = ""
    for ch in text:
        rep = ch
        if ch in mapping:
            rep = rng.choice(_variants(ch, level, rng, mapping))
        elif level >= 2 and ch.isascii() and ch.isalpha():
            rep = chr(ord(ch) + 0xFEE0)  # 全角
        elif level >= 3 and ch in CIRCLED:
            rep = CIRCLED[ch] if rng.random() < 0.4 else ch
        out.append(rep)
        if level >= 2:
            p = 0.25 if level == 2 else 0.55
            if rng.random() < p:
                sym = rng.choice(SYMBOLS)
                if sym != last_sym:
                    out.append(sym)
                    last_sym = sym
    return "".join(out)


CIRCLED_HAN = {c: z for c, z in zip("①②③④⑤⑥⑦⑧⑨⑩", "一二三四五六七八九十")}


def restore(text, dict_mode="builtin"):
    text = "".join(CIRCLED_HAN.get(c, c) for c in text)  # 带圈数字回汉字，再走 NFKC
    t = unicodedata.normalize("NFKC", text)
    rev = get_rev(dict_mode)
    out = []
    for ch in t:
        if ch in rev:
            out.append(rev[ch])
        elif ch in SYMBOLS:
            continue
        elif ch in " \t\u3000":
            out.append(" ")
        elif "\u4e00" <= ch <= "\u9fff" or ch.isascii():
            out.append(ch)
        # 其余 emoji / 装饰字符丢弃
    s = re.sub(r"\s+", " ", "".join(out)).strip()
    if not re.search(r"[A-Za-z]", s):
        s = s.replace(" ", "")
    return s


def main():
    ap = argparse.ArgumentParser(description="火星文转换 / 还原")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("convert", help="正常中文 -> 火星文")
    c.add_argument("text", nargs="?", help="待转换文本；省略则读 stdin")
    c.add_argument("--level", type=int, default=2, choices=[1, 2, 3], help="1 轻 / 2 中 / 3 重")
    c.add_argument("--seed", default=None, help="随机种子，用于复现同一结果")
    c.add_argument("--dict", default="builtin", choices=["builtin", "full"], dest="dict_mode",
                   help="builtin 手工精选 196 条 / full 全量 2000+ 条（还原有歧义）")

    r = sub.add_parser("restore", help="火星文 -> 正常中文")
    r.add_argument("text", nargs="?", help="待还原文本；省略则读 stdin")
    r.add_argument("--dict", default="builtin", choices=["builtin", "full"], dest="dict_mode",
                   help="builtin 手工精选 / full 全量（冲突字按索引取靠前的简体）")

    a = ap.parse_args()
    text = a.text if a.text else sys.stdin.read()

    if a.cmd == "convert":
        print(convert(text, a.level, a.seed, a.dict_mode))
    else:
        print(restore(text, a.dict_mode))


if __name__ == "__main__":
    main()

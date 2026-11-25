# 火星文 Skill · huoxingwen

[![CI](https://github.com/hhym/huoxingwen-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/hhym/huoxingwen-skill/actions/workflows/ci.yml)

简体中文 ⇄ 火星文 双向转换。按 [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) 的目录规范组织（`SKILL.md` + `scripts/` + `references/`），可直接放进 `.user_skills/` 给 AI 用，也可以当独立 Python 工具跑。

## 能力

- **正向**：正常中文 → 火星文，三档强度（轻度只换异体字、中度加符号点缀、重度叠加假名/带圈数字/全角字母）
- **反向**：火星文 → 可读中文，自动清理装饰符号、归一化全角、把带圈数字还原成汉字
- **可复现**：`--seed` 固定随机种子，批量生成结果一致

## 快速开始

```bash
python3 scripts/huoxingwen.py convert "我爱你，永远守护你" --level 2 --seed 7
# 莪愛妳,☆咏逺•垨護ヾ妳

python3 scripts/huoxingwen.py convert "长文本……" --dict full
# 全量表，2096 条映射，火星味更足

python3 scripts/huoxingwen.py restore "為什仫莪啲裏屋囷伱們啲鈈┅樣"
# 为什么我的里屋困你们的不一样
```

不传文本参数时从 stdin 读，方便接管道：

```bash
echo "今天也要好好生活" | python3 scripts/huoxingwen.py convert --level 2
```

## 两套字典

| 模式 | 条目 | 用途 | 说明 |
| --- | --- | --- | --- |
| `builtin`（默认） | 196 | 昵称、签名、短文案 | 手工精选，变形可控，还原准确 |
| `full` | 2096 | 长文、标题、整段改写 | 由 3815 位三表转换，覆盖广但形近字会串 |

`full` 模式有 310 组一对多冲突（同一个火星字对应多个简体字，如 `妑` ← 芭/吧/巴/把/爸），按拼音索引取靠前的简体。冲突清单在 `references/mars_conflicts.csv`，要求精确还原时请用默认模式或先查表。

## 目录

```
SKILL.md                  # 给 AI 的指令与边界
scripts/huoxingwen.py     # 主程序，零依赖
scripts/mars_dict.py      # 3815 位三表数据（简体/繁体/火星文）
references/mars_conflicts.csv  # 310 组还原歧义清单
```

## 数据来源

- 手工精选 196 条：网络常见火星文对照（莪/伱/の/叻/恏 之类）
- 全量三表：来自 [Niefee/textConversion](https://github.com/Niefee/textConversion) 的 `a.js`，已校验 3815 位逐位对齐，剔除其中 373 位实为繁体的项
- 部分变体来自 MNBVC 里屋论坛语料的抽样（仫/啲/孓/昰/葑/掱/楿 等）

## 边界

- 装饰符号会丢，`520` / `1314` 这类谐音数字不展开
- 粤语书面字（啲、叻、哋、噫）与火星文同形，会被一并还原成普通话
- 不要把正常繁体文本当火星文还原，它会被转成简体

## 许可

MIT

## 致谢

本项目的数据与代码基础来自这两个开源项目，均为 MIT 许可，与本项目兼容：

- [Niefee/textConversion](https://github.com/Niefee/textConversion) —— 简体字、繁体字与火星文相互转换。`scripts/mars_dict.py` 的 3815 位三表（简体 / 繁体 / 火星文）即由该项目的 `a.js` 转换而来，本项目做了逐位对齐校验、繁体项剔除、O(1) 查表改造。
- [esbatmop/MNBVC](https://github.com/esbatmop/MNBVC) —— 超大规模中文语料集。`builtin` 手工表中有 15 个字条、8 个变体取自其里屋论坛语料的真实用例抽样（仫 / 啲 / 孓 / 昰 / 葑 / 掱 / 楿 / 嫆 / 噫 / 箌 / 脳 等）。

## 测试

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 在每次 push / PR 时自动跑 9 项测试：三档回环、种子可复现、全量表条目数、带圈数字还原、符号清理、SKILL.md frontmatter、冲突表行数。

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import huoxingwen as h  # noqa: E402


class TestConvert(unittest.TestCase):
    def test_roundtrip_all_levels(self):
        text = "我爱你永远守护你"
        for level in (1, 2, 3):
            out = h.convert(text, level, seed=7)
            self.assertTrue(out)
            self.assertNotEqual(out, text)
            self.assertEqual(h.restore(out), text)

    def test_seed_is_deterministic(self):
        a = h.convert("寂寞的夜晚想起你", 2, seed=42)
        b = h.convert("寂寞的夜晚想起你", 2, seed=42)
        self.assertEqual(a, b)

    def test_levels_differ(self):
        a = h.convert("我爱你每一天", 1, seed=1)
        b = h.convert("我爱你每一天", 3, seed=1)
        self.assertNotEqual(a, b)


class TestFlower(unittest.TestCase):
    STYLES = ["vine", "messy", "germinate", "fog", "prohibit", "grass", "wind"]

    def test_styles_wrap_and_strip(self):
        for s in self.STYLES:
            out = h.flower("花漾字", s)
            self.assertGreater(len(out), 3)
            self.assertEqual(h.strip_flower(out), "花漾字")
            self.assertEqual(h.restore(out), "花漾字")

    def test_style_markers(self):
        self.assertEqual(h.flower("字", "vine"), "ζั͡字ั͡✾")
        self.assertEqual(h.flower("字", "messy"), "҉҉҉字҉҉҉")
        self.assertEqual(h.flower("字", "prohibit"), "字⃠")
        self.assertEqual(h.flower("字", "wind"), "=͟͟͞͞字")

    def test_mars_preset(self):
        # 与语燕输入法 FlowerPreset 同款的直映射
        self.assertEqual(h.flower("火星文", "mars"), "焱暒妏")
        self.assertEqual(h.flower("ABCD1", "mars"), "ＡвсＤ①")

    def test_convert_then_flower(self):
        out = h.convert("我爱你", 1, seed=3, flower_style="vine")
        self.assertTrue(out.startswith("ζั͡"))
        self.assertEqual(h.restore(out), "我爱你")


class TestDicts(unittest.TestCase):
    def test_full_table_size(self):
        m, r = h._full_tables()
        self.assertEqual(len(m), 2096)
        self.assertEqual(len(r), 1681)

    def test_full_convert_changes_text(self):
        src = "我爱你每一天"
        self.assertNotEqual(h.convert(src, 2, seed=5, dict_mode="full"), src)

    def test_circled_digit_to_han(self):
        self.assertEqual(h.restore("①"), "一")
        self.assertEqual(h.restore("⑨"), "九")

    def test_symbols_stripped(self):
        self.assertEqual(h.restore("莪☆愛ゞ伱"), "我爱你")


class TestFiles(unittest.TestCase):
    def test_skill_frontmatter(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---"))
        head = text.split("---", 2)[1]
        self.assertIn("name: huoxingwen", head)
        self.assertIn("description:", head)
        self.assertGreater(len(head.split("description:", 1)[1].strip()), 20)

    def test_conflicts_table(self):
        lines = (ROOT / "references" / "mars_conflicts.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "火星字,候选简体,冲突数")
        self.assertEqual(len(lines) - 1, 310)


if __name__ == "__main__":
    unittest.main()

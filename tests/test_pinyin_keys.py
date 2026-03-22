import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pinyin_data import build_search_keys, to_pinyin, to_initials


def test_system_settings_keys():
    """系统 -> xitong, xt"""
    keys = build_search_keys("系统")
    assert keys["original"] == "系统"
    assert "xitong" in keys["full_pinyin"]
    assert "xt" in keys["initials"]


def test_to_pinyin_simple():
    assert to_pinyin("系统") == "xitong"
    assert to_pinyin("设置") == "shezhi"


def test_to_initials_simple():
    assert to_initials("系统") == "xt"
    assert to_initials("设置") == "sz"


def test_non_chinese_pass_through():
    """Non-Chinese text should pass through unchanged or just lowercased."""
    result = to_pinyin("Chrome")
    assert "chrome" in result.lower()


def test_mixed_chinese_english():
    """Mixed content should handle both."""
    keys = build_search_keys("系统设置中心")
    assert "zhongxin" in keys["full_pinyin"]


def test_settings_center():
    """设置中心 -> shezhizhongxin, szx"""
    keys = build_search_keys("设置中心")
    assert keys["full_pinyin"] == "shezhizhongxin"
    assert keys["initials"] == "szx"


def test_chrome_english():
    """English names should return lowercase."""
    keys = build_search_keys("Chrome")
    assert keys["full_pinyin"] == "chrome"
    assert keys["initials"] == "c"


def test_mixed_name():
    """Test mixed Chinese and English app names."""
    keys = build_search_keys("微信WeChat")
    # Should contain both pinyin and english
    assert (
        "weixin" in keys["full_pinyin"].lower()
        or "wechat" in keys["full_pinyin"].lower()
    )


def test_common_apps():
    """Test some common Chinese app names."""
    # 浏览器
    keys = build_search_keys("浏览器")
    assert "liulanqi" in keys["full_pinyin"]
    assert "llq" in keys["initials"]

    # 文件管理器
    keys = build_search_keys("文件管理器")
    assert "wenjianguanliqi" in keys["full_pinyin"]
    assert "wjglq" in keys["initials"]


def test_empty_string():
    """Empty string should return empty results."""
    keys = build_search_keys("")
    assert keys["original"] == ""
    assert keys["full_pinyin"] == ""
    assert keys["initials"] == ""


def test_punctuation():
    """Punctuation should pass through."""
    result = to_pinyin("设置-中心")
    assert "shezhi" in result
    assert "-" in result

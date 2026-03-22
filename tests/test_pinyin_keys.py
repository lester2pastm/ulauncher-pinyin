import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pinyin_data import build_search_keys, to_pinyin, to_initials


TOP_LINUX_APP_CHINESE_NAMES = [
    "火狐浏览器",
    "谷歌浏览器",
    "浏览器",
    "自由办公",
    "办公套件",
    "雷鸟邮件",
    "邮件客户端",
    "钉钉",
    "微信",
    "媒体播放器",
    "音频编辑器",
    "音乐播放器",
    "网易云音乐",
    "图像处理软件",
    "矢量图形编辑器",
    "绘画软件",
    "三维图形软件",
    "照片处理器",
    "代码编辑器",
    "文本编辑器",
    "文件管理器",
    "终端",
    "下拉式终端",
    "云存储",
    "云盘",
    "下载管理器",
    "虚拟机",
    "分区编辑器",
    "优化工具",
    "系统清理",
    "防火墙",
    "截图工具",
    "录屏工具",
    "视频编辑器",
    "包管理器",
    "软件中心",
    "设置中心",
    "系统监视器",
    "磁盘管理器",
    "归档管理器",
    "计算器",
    "日历",
    "便笺",
    "扫描器",
    "摄像头",
    "远程桌面",
    "备份工具",
    "密码管理器",
    "输入法",
    "应用商店",
]


def _contains_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


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


def test_lanxin_simplified_name():
    keys = build_search_keys("蓝信")
    assert keys["full_pinyin"] == "lanxin"
    assert keys["initials"] == "lx"


def test_music_uses_yue_pronunciation():
    keys = build_search_keys("音乐")
    assert keys["full_pinyin"] == "yinyue"
    assert keys["initials"] == "yy"


def test_netease_cloud_music_uses_yue_pronunciation():
    keys = build_search_keys("网易云音乐")
    assert keys["full_pinyin"] == "wangyiyunyinyue"
    assert keys["initials"] == "wyyyy"


def test_letian_keeps_default_le_pronunciation_outside_music_phrase():
    keys = build_search_keys("乐天")
    assert keys["full_pinyin"] == "letian"
    assert keys["initials"] == "lt"


def test_top_linux_app_names_are_fully_mapped_to_pinyin():
    for name in TOP_LINUX_APP_CHINESE_NAMES:
        full = to_pinyin(name)
        initials = to_initials(name)
        assert not _contains_chinese(full), (name, full)
        assert not _contains_chinese(initials), (name, initials)


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

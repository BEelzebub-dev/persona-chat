#!/usr/bin/env python3
"""
persona-chat 激活脚本
用于在群聊/私聊中切换人格角色
"""

import json
import os
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
CHARACTERS_DIR = SKILL_DIR / "scripts" / "characters"
STATE_FILE = Path.home() / ".openclaw" / "workspace" / ".persona_state.json"

VALID_CHARACTERS = [
    "yinyue", "zigling", "yuanyao", "nangongwan", "baiyaoyi",
    "meining", "mupilling", "liulele", "tihun"
]

CHARACTER_DISPLAY_NAMES = {
    "yinyue": "银月",
    "zigling": "紫灵",
    "yuanyao": "元瑶",
    "nangongwan": "南宫婉",
    "baiyaoyi": "白瑶怡",
    "meining": "梅凝",
    "mupilling": "慕沛灵",
    "liulele": "柳乐儿",
    "tihun": "啼魂",
}


def load_state():
    """加载人格状态"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"[persona-chat] 加载状态失败: {e}")
        return {}


def save_state(state):
    """保存人格状态"""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[persona-chat] 保存状态失败: {e}")
        return False


def load_character(character_name):
    """加载角色设定文件"""
    char_file = CHARACTERS_DIR / f"{character_name}.md"
    if not char_file.exists():
        return None
    try:
        with open(char_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[persona-chat] 读取角色文件失败: {e}")
        return None


def list_characters():
    """列出所有可用角色"""
    characters = []
    for char_file in CHARACTERS_DIR.glob("*.md"):
        name = char_file.stem
        display = CHARACTER_DISPLAY_NAMES.get(name, name)
        characters.append({"id": name, "display": display})
    return characters


def switch_persona(chat_id, character_name):
    """
    切换人格
    :param chat_id: 群聊或私聊ID
    :param character_name: 角色名（如 yinyue）
    :return: (success, message)
    """
    if character_name not in VALID_CHARACTERS:
        valid_list = ", ".join(VALID_CHARACTERS)
        return False, f"未知角色：「{character_name}」。可用角色：{valid_list}"

    character_content = load_character(character_name)
    if not character_content:
        return False, f"加载角色「{character_name}」失败，角色文件不存在"

    state = load_state()
    state[chat_id] = character_name
    if save_state(state):
        display_name = CHARACTER_DISPLAY_NAMES.get(character_name, character_name)
        return True, f"已切换为「{display_name}」人格"
    else:
        return False, "切换人格失败，无法保存状态"


def exit_persona(chat_id):
    """
    退出人格，恢复小虾米
    :param chat_id: 群聊或私聊ID
    :return: (success, message)
    """
    state = load_state()
    if chat_id in state:
        old_persona = state.pop(chat_id)
        if save_state(state):
            old_display = CHARACTER_DISPLAY_NAMES.get(old_persona, old_persona)
            return True, f"已退出「{old_display}」人格，恢复小虾米模式"
    return True, "当前已是小虾米人格"


def get_current_persona(chat_id):
    """
    获取当前人格
    :param chat_id: 群聊或私聊ID
    :return: 角色名或 None（小虾米）
    """
    state = load_state()
    return state.get(chat_id)


def get_persona_info(chat_id):
    """
    获取当前人格详细信息
    :param chat_id: 群聊或私聊ID
    :return: (is_persona, character_name, character_content)
    """
    persona = get_current_persona(chat_id)
    if persona:
        content = load_character(persona)
        display = CHARACTER_DISPLAY_NAMES.get(persona, persona)
        return True, display, content
    return False, "小虾米", None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 activate_persona.py <command> [args]")
        print("命令:")
        print("  list                           - 列出所有角色")
        print("  switch <chat_id> <character>  - 切换人格")
        print("  exit <chat_id>                 - 退出人格")
        print("  current <chat_id>              - 获取当前人格")
        print("  info <chat_id>                 - 获取人格详情")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        chars = list_characters()
        for c in chars:
            print(f"  {c['id']} - {c['display']}")

    elif cmd == "switch" and len(sys.argv) >= 4:
        chat_id = sys.argv[2]
        character = sys.argv[3]
        ok, msg = switch_persona(chat_id, character)
        print(msg)
        sys.exit(0 if ok else 1)

    elif cmd == "exit" and len(sys.argv) >= 3:
        chat_id = sys.argv[2]
        ok, msg = exit_persona(chat_id)
        print(msg)

    elif cmd == "current" and len(sys.argv) >= 3:
        chat_id = sys.argv[2]
        persona = get_current_persona(chat_id)
        if persona:
            display = CHARACTER_DISPLAY_NAMES.get(persona, persona)
            print(f"当前人格: {display}")
        else:
            print("当前人格: 小虾米")

    elif cmd == "info" and len(sys.argv) >= 3:
        chat_id = sys.argv[2]
        is_p, name, content = get_persona_info(chat_id)
        print(f"当前人格: {name}")
        if content:
            print("\n角色设定:")
            print(content)

    else:
        print("参数不足或命令错误")
        sys.exit(1)

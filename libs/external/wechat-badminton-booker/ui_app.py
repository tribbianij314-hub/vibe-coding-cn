#!/usr/bin/env python3
"""羽毛球预约可视化配置与执行界面（Streamlit）。"""

from __future__ import annotations

import datetime as dt
import itertools
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import streamlit as st
import yaml

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.yaml"


def split_csv(text: str) -> list[str]:
    if not text.strip():
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def dedupe_pairs(items: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for pair in items:
        if pair not in seen:
            seen.add(pair)
            out.append(pair)
    return out


def build_priority_pairs(target_court: str, target_slot: str, fallback_courts: list[str], fallback_slots: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = [(target_court, target_slot)]
    pairs.extend((court, target_slot) for court in fallback_courts)
    pairs.extend((target_court, slot) for slot in fallback_slots)
    pairs.extend((court, slot) for court, slot in itertools.product(fallback_courts, fallback_slots))
    return dedupe_pairs(pairs)


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_config(path: Path, config: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)


def run_booking(config_path: Path) -> int:
    cmd = [sys.executable, str(BASE_DIR / "pc_booker.py"), "--config", str(config_path)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(BASE_DIR))
    output_box = st.empty()
    logs: list[str] = []

    assert proc.stdout is not None
    for line in proc.stdout:
        logs.append(line.rstrip("\n"))
        output_box.code("\n".join(logs[-200:]), language="bash")

    proc.wait(timeout=5)
    return proc.returncode


def main() -> None:
    st.set_page_config(page_title="羽毛球预约助手", page_icon="🏸", layout="wide")
    st.title("🏸 羽毛球场地预约助手（电脑端）")
    st.caption("适用于 Playwright 自动化流程：先配置，再在 23:00 自动执行。")

    initial = load_config(DEFAULT_CONFIG_PATH)
    runtime = initial.get("runtime", {})
    booking = initial.get("booking", {})
    selectors = initial.get("selectors", {})

    with st.sidebar:
        st.subheader("快捷说明")
        st.markdown(
            """
            1. 先填写 URL 与选择器。
            2. 点击 **保存配置**。
            3. 点击 **启动预约**，脚本会等待到放号时间。
            4. 首次建议开启“手动登录后继续”。
            """
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("运行参数")
        url = st.text_input("预约入口 URL", value=runtime.get("url", "https://xcx-api.zuduijun.com/api/long-url?code=AzYr2i&app=13"))
        start_at = st.text_input("放号时间 (HH:MM:SS)", value=runtime.get("start_at", "23:00:00"))
        headless = st.checkbox("无头模式（不显示浏览器）", value=runtime.get("headless", False))
        manual_login = st.checkbox("手动登录后继续", value=runtime.get("manual_login", True))
        default_timeout_ms = st.number_input("元素超时(ms)", min_value=100, max_value=5000, value=int(runtime.get("default_timeout_ms", 600)), step=50)
        click_delay_ms = st.number_input("点击间隔(ms)", min_value=1, max_value=200, value=int(runtime.get("click_delay_ms", 20)), step=1)
        max_attempts_per_combo = st.number_input("每个组合重试次数", min_value=1, max_value=20, value=int(runtime.get("max_attempts_per_combo", 3)), step=1)

        st.subheader("预约策略")
        advance_days = st.number_input("提前预约天数", min_value=1, max_value=15, value=int(booking.get("advance_days", 2)), step=1)
        target_court = st.text_input("首选场地", value=booking.get("target_court", "1号场"))
        target_slot = st.text_input("首选时段", value=booking.get("target_slot", "18:00-19:00"))
        fallback_courts = st.text_input("候补场地（逗号分隔）", value=", ".join(booking.get("fallback_courts", ["2号场", "3号场", "4号场", "5号场", "6号场"])))
        fallback_slots = st.text_input("候补时段（逗号分隔）", value=", ".join(booking.get("fallback_slots", ["19:00-20:00", "17:00-18:00", "20:00-21:00"])))
        submit_texts = st.text_input("提交按钮文案（逗号分隔）", value=", ".join(initial.get("submit_texts", ["立即预约", "确认预约", "提交", "去支付"])))

    with col2:
        st.subheader("页面选择器")
        booking_entry = st.text_input("预约入口（可空）", value=selectors.get("booking_entry", ""))
        date_cell = st.text_input("日期选择器模板", value=selectors.get("date_cell", "[data-date='{date}']"))
        court_cell = st.text_input("场地选择器模板", value=selectors.get("court_cell", "xpath=//*[contains(normalize-space(.), '{court}')]"))
        slot_cell = st.text_input("时段选择器模板", value=selectors.get("slot_cell", "xpath=//*[contains(normalize-space(.), '{slot}')]"))

        target_date = dt.date.today() + dt.timedelta(days=int(advance_days))
        st.info(f"按当前配置，目标日期将是：**{target_date.isoformat()}**")

        preview_pairs = build_priority_pairs(
            target_court=target_court,
            target_slot=target_slot,
            fallback_courts=split_csv(fallback_courts),
            fallback_slots=split_csv(fallback_slots),
        )
        st.subheader("候选顺序预览")
        st.dataframe(
            [{"优先级": idx + 1, "场地": p[0], "时段": p[1]} for idx, p in enumerate(preview_pairs)],
            use_container_width=True,
            hide_index=True,
        )

    config = {
        "runtime": {
            "url": url,
            "start_at": start_at,
            "headless": bool(headless),
            "manual_login": bool(manual_login),
            "default_timeout_ms": int(default_timeout_ms),
            "click_delay_ms": int(click_delay_ms),
            "max_attempts_per_combo": int(max_attempts_per_combo),
        },
        "booking": {
            "advance_days": int(advance_days),
            "target_court": target_court,
            "target_slot": target_slot,
            "fallback_courts": split_csv(fallback_courts),
            "fallback_slots": split_csv(fallback_slots),
        },
        "submit_texts": split_csv(submit_texts),
        "selectors": {
            "booking_entry": booking_entry,
            "date_cell": date_cell,
            "court_cell": court_cell,
            "slot_cell": slot_cell,
        },
    }

    action1, action2 = st.columns(2)
    with action1:
        if st.button("💾 保存配置", use_container_width=True):
            save_config(DEFAULT_CONFIG_PATH, config)
            st.success(f"配置已保存：{DEFAULT_CONFIG_PATH}")

    with action2:
        if st.button("🚀 启动预约", use_container_width=True):
            save_config(DEFAULT_CONFIG_PATH, config)
            st.warning("任务启动中：请勿关闭本页面，日志将实时显示。")
            code = run_booking(DEFAULT_CONFIG_PATH)
            if code == 0:
                st.success("脚本执行完成。请核对订单状态。")
            else:
                st.error(f"脚本异常退出，退出码：{code}")


if __name__ == "__main__":
    main()

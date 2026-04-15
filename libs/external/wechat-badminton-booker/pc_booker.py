#!/usr/bin/env python3
"""电脑端羽毛球场地预约脚本（Playwright 版）。

使用方式：
  1) cp config.example.yaml config.yaml
  2) 按目标小程序/网页实际结构填写选择器与文案
  3) python pc_booker.py --config config.yaml

说明：
- 该脚本默认通过浏览器自动化进行抢位，不依赖公开 API。
- 若目标系统存在验证码、短信二次校验、人机风控等机制，需人工介入。
"""

from __future__ import annotations

import argparse
import datetime as dt
import itertools
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright


@dataclass(frozen=True)
class BookingTarget:
    court: str
    slot: str


class BookingBot:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.runtime = cfg["runtime"]
        self.booking = cfg["booking"]
        self.selectors = cfg["selectors"]
        self.submit_texts = cfg["submit_texts"]

    def run(self) -> None:
        start_at = self._resolve_target_time(self.runtime["start_at"])
        self._wait_until(start_at)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.runtime.get("headless", False))
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(int(self.runtime.get("default_timeout_ms", 600)))

            self._open_and_prepare(page)
            ok = self._attempt_booking(page)
            browser.close()

        if ok:
            print("[SUCCESS] 已点击到提交/确认按钮，请立即检查订单页状态。")
        else:
            print("[FAILED] 所有候选组合均未命中可提交状态，请手动检查。")

    def _open_and_prepare(self, page: Page) -> None:
        target_url = self.runtime["url"]
        print(f"[INFO] 打开页面: {target_url}")
        page.goto(target_url, wait_until="domcontentloaded")

        if self.runtime.get("manual_login", True):
            print("[ACTION] 请在浏览器中手动完成登录，然后在终端按回车继续...", flush=True)
            input()

        if self.selectors.get("booking_entry"):
            self._click_selector(page, self.selectors["booking_entry"])

    def _attempt_booking(self, page: Page) -> bool:
        reserve_date = self._target_date()
        print(f"[INFO] 预约日期: {reserve_date}")

        date_template = self.selectors["date_cell"]
        self._click_selector(page, date_template.format(date=reserve_date))

        pairs = self._build_priority_pairs()
        print(f"[INFO] 待尝试组合数: {len(pairs)}")

        for index, pair in enumerate(pairs, start=1):
            print(f"[TRY] {index}/{len(pairs)} -> 场地={pair.court}, 时段={pair.slot}")
            for _ in range(int(self.runtime.get("max_attempts_per_combo", 2))):
                if self._try_one_pair(page, pair):
                    return True
                time.sleep(self._jitter())

        return False

    def _try_one_pair(self, page: Page, pair: BookingTarget) -> bool:
        court_selector = self.selectors["court_cell"].format(court=pair.court)
        slot_selector = self.selectors["slot_cell"].format(slot=pair.slot)

        self._click_selector(page, court_selector, silent=True)
        time.sleep(self._jitter())
        self._click_selector(page, slot_selector, silent=True)
        time.sleep(self._jitter())

        for text in self.submit_texts:
            if self._click_by_text(page, text):
                print(f"[HIT] 命中提交按钮文案: {text}")
                return True
        return False

    def _click_by_text(self, page: Page, text: str) -> bool:
        try:
            locator = page.get_by_text(text, exact=False)
            if locator.count() > 0:
                locator.first.click()
                return True
        except PlaywrightTimeoutError:
            return False
        return False

    def _click_selector(self, page: Page, selector: str, silent: bool = False) -> bool:
        try:
            page.locator(selector).first.click()
            return True
        except PlaywrightTimeoutError:
            if not silent:
                print(f"[WARN] 未找到选择器: {selector}")
            return False

    def _build_priority_pairs(self) -> list[BookingTarget]:
        primary = BookingTarget(
            court=self.booking["target_court"],
            slot=self.booking["target_slot"],
        )
        fallback_courts = self.booking.get("fallback_courts", [])
        fallback_slots = self.booking.get("fallback_slots", [])

        ordered: list[BookingTarget] = [primary]
        ordered.extend(BookingTarget(court=c, slot=primary.slot) for c in fallback_courts)
        ordered.extend(BookingTarget(court=primary.court, slot=s) for s in fallback_slots)
        ordered.extend(BookingTarget(court=c, slot=s) for c, s in itertools.product(fallback_courts, fallback_slots))

        return self._dedupe(ordered)

    @staticmethod
    def _dedupe(items: Iterable[BookingTarget]) -> list[BookingTarget]:
        out: list[BookingTarget] = []
        seen: set[tuple[str, str]] = set()
        for item in items:
            key = (item.court, item.slot)
            if key not in seen:
                seen.add(key)
                out.append(item)
        return out

    def _target_date(self) -> str:
        # 提前两天预约
        offset_days = int(self.booking.get("advance_days", 2))
        target = dt.date.today() + dt.timedelta(days=offset_days)
        return target.isoformat()

    @staticmethod
    def _resolve_target_time(start_at: str) -> dt.datetime:
        now = dt.datetime.now()
        hh, mm, ss = (int(v) for v in start_at.split(":"))
        target = now.replace(hour=hh, minute=mm, second=ss, microsecond=0)
        if target <= now:
            return now
        return target

    @staticmethod
    def _wait_until(target: dt.datetime) -> None:
        if target <= dt.datetime.now():
            print("[INFO] 目标时间已到，立即执行。")
            return

        print(f"[INFO] 等待至 {target.strftime('%Y-%m-%d %H:%M:%S')} 开始抢位...")
        while True:
            remain = (target - dt.datetime.now()).total_seconds()
            if remain <= 0:
                break
            if remain > 5:
                if int(remain) % 5 == 0:
                    print(f"[T-] 剩余 {int(remain)} 秒")
                time.sleep(0.2)
            elif remain > 1:
                time.sleep(0.05)
            else:
                time.sleep(0.01)
        print("[INFO] 到点，开始执行。")

    def _jitter(self) -> float:
        base = float(self.runtime.get("click_delay_ms", 20)) / 1000
        return max(0.005, base + random.uniform(0, 0.015))


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="电脑端羽毛球预约脚本（Playwright）")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(Path(args.config))
    bot = BookingBot(cfg)
    bot.run()


if __name__ == "__main__":
    main()

"ui";

/**
 * 微信小程序羽毛球预约脚本（Auto.js）
 *
 * 使用前请先阅读同目录 README.md。
 */

const CONFIG = {
  // 放号时间（24 小时制）
  startAt: "23:00:00",

  // 首选
  targetCourt: "1号场",
  targetSlot: "18:00-19:00",

  // 候补（按顺序尝试）
  fallbackCourts: ["2号场", "3号场", "4号场", "5号场", "6号场"],
  fallbackSlots: ["19:00-20:00", "17:00-18:00", "20:00-21:00", "16:00-17:00", "15:00-16:00"],

  // 可能出现的按钮文案
  submitTexts: ["立即预约", "确认预约", "提交", "去支付"],

  // 点击与重试
  clickDelayMs: 25,
  searchTimeoutMs: 180,
  maxAttemptsPerCombo: 3,
};

function main() {
  auto.waitFor();
  console.show();
  console.log("=== 羽毛球预约脚本启动 ===");

  waitUntilTargetTime(CONFIG.startAt);
  device.vibrate(100);

  const pairs = buildPriorityPairs();
  console.log(`组合总数：${pairs.length}`);

  let success = false;

  for (let i = 0; i < pairs.length; i += 1) {
    const pair = pairs[i];
    console.log(`尝试 ${i + 1}/${pairs.length} -> ${pair.court} / ${pair.slot}`);

    for (let j = 0; j < CONFIG.maxAttemptsPerCombo; j += 1) {
      const ok = tryBook(pair.court, pair.slot);
      if (ok) {
        success = true;
        break;
      }
      sleep(CONFIG.clickDelayMs);
    }

    if (success) {
      break;
    }
  }

  if (success) {
    toast("疑似预约成功，请立即核对订单状态");
    device.vibrate(300);
    console.log("已命中提交按钮，流程结束。请人工确认结果。\n");
  } else {
    toast("未命中可提交状态，请手动检查");
    device.vibrate(300);
    sleep(120);
    device.vibrate(300);
    console.log("所有候选组合尝试完成，未进入提交状态。\n");
  }
}

function waitUntilTargetTime(targetTime) {
  const [hh, mm, ss] = targetTime.split(":").map((v) => parseInt(v, 10));
  const now = new Date();

  const target = new Date(now.getTime());
  target.setHours(hh, mm, ss, 0);

  if (target.getTime() <= now.getTime()) {
    console.log("目标时间已过，立即执行。\n");
    return;
  }

  console.log(`等待至 ${target.toLocaleTimeString()} 开始抢场...`);

  while (true) {
    const remain = target.getTime() - Date.now();
    if (remain <= 0) {
      break;
    }

    if (remain > 1000) {
      if (remain % 5000 < 1000) {
        console.log(`倒计时 ${Math.ceil(remain / 1000)} 秒`);
      }
      sleep(200);
    } else {
      sleep(20);
    }
  }

  console.log("到点，开始执行点击。\n");
}

function buildPriorityPairs() {
  const list = [{ court: CONFIG.targetCourt, slot: CONFIG.targetSlot }];

  for (let i = 0; i < CONFIG.fallbackCourts.length; i += 1) {
    list.push({ court: CONFIG.fallbackCourts[i], slot: CONFIG.targetSlot });
  }

  for (let j = 0; j < CONFIG.fallbackSlots.length; j += 1) {
    list.push({ court: CONFIG.targetCourt, slot: CONFIG.fallbackSlots[j] });
  }

  for (let a = 0; a < CONFIG.fallbackCourts.length; a += 1) {
    for (let b = 0; b < CONFIG.fallbackSlots.length; b += 1) {
      list.push({ court: CONFIG.fallbackCourts[a], slot: CONFIG.fallbackSlots[b] });
    }
  }

  return dedupePairs(list);
}

function dedupePairs(pairs) {
  const seen = {};
  const output = [];

  for (let i = 0; i < pairs.length; i += 1) {
    const k = `${pairs[i].court}@@${pairs[i].slot}`;
    if (!seen[k]) {
      seen[k] = true;
      output.push(pairs[i]);
    }
  }

  return output;
}

function tryBook(courtText, slotText) {
  clickByTextContains(courtText);
  sleep(CONFIG.clickDelayMs);

  clickByTextContains(slotText);
  sleep(CONFIG.clickDelayMs);

  for (let i = 0; i < CONFIG.submitTexts.length; i += 1) {
    if (clickByTextContains(CONFIG.submitTexts[i])) {
      console.log(`命中提交按钮：${CONFIG.submitTexts[i]}`);
      return true;
    }
  }

  return false;
}

function clickByTextContains(t) {
  const node = textContains(t).findOne(CONFIG.searchTimeoutMs);
  if (!node) {
    return false;
  }

  const clickableParent = findClickableParent(node);
  if (clickableParent) {
    clickableParent.click();
    return true;
  }

  const b = node.bounds();
  click(b.centerX(), b.centerY());
  return true;
}

function findClickableParent(node) {
  let cur = node;
  let depth = 0;

  while (cur && depth < 6) {
    if (cur.clickable()) {
      return cur;
    }
    cur = cur.parent();
    depth += 1;
  }

  return null;
}

main();

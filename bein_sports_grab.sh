#!/usr/bin/env bash
set -e

# 1. 拉取 iptv-org/epg
if [ ! -d "iptv-org-epg" ]; then
  git clone --depth 1 https://github.com/iptv-org/epg.git iptv-org-epg
fi

cd iptv-org-epg

# 2. 安装依赖
npm install

# 3. 抓取 beIN 全球（MENA + US + FR + AU + MY + NZ…）
# iptv-org 会自动读取 sites/beinsports.com 下所有地区
npm run grab -- --site=beinsports.com --days=3 --output=../bein_sports_raw.xml

cd ..

const { execSync } = require('child_process')
const fs = require('fs')

// 自动装依赖给 config.js 用
function ensure(pkg) {
  try { require.resolve(pkg) }
  catch {
    console.log(`Installing ${pkg}...`)
    execSync(`npm install ${pkg}`, { stdio: 'inherit' })
  }
}
ensure('axios')
ensure('dayjs')

// beIN 全区
const regions = [
  'beinsports.com_mena-en',
  'beinsports.com_us-en',
  'beinsports.com_fr-fr',
  'beinsports.com_au-en',
  'beinsports.com_my-en',
  'beinsports.com_nz-en'
]

// 目录
if (!fs.existsSync('tmp')) fs.mkdirSync('tmp')
if (!fs.existsSync('output')) fs.mkdirSync('output')

// 抓取每个区 → 单独 XML
for (const r of regions) {
  console.log('Fetching', r)
  execSync(
    `npx epg-grabber ` +
    `--config=epg_beinsports/beinsports.com.config.js ` +
    `--channels=epg_beinsports/${r}.channels.xml ` +
    `--output=tmp/${r}.xml`,
    { stdio: 'inherit' }
  )
}

// 用 Python 合并（稳定 & 可控）
console.log('Merging XML with Python...')
execSync('python epg_beinsports_merge.py', { stdio: 'inherit' })

console.log('✅ beIN 全区 EPG 生成完成')

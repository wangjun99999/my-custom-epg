const { execSync } = require('child_process')
const fs = require('fs')

// ----------------------------
// 自动安装依赖（给 config.js 用）
// ----------------------------
function ensure(pkg) {
  try {
    require.resolve(pkg)
  } catch {
    console.log(`${pkg} 不存在，正在安装...`)
    execSync(`npm install ${pkg}`, { stdio: 'inherit' })
  }
}

ensure('axios')
ensure('dayjs')

// ----------------------------
// beIN 全区
// ----------------------------
const regions = [
  'beinsports.com_mena-en',
  'beinsports.com_us-en',
  'beinsports.com_fr-fr',
  'beinsports.com_au-en',
  'beinsports.com_my-en',
  'beinsports.com_nz-en'
]

// ----------------------------
// 目录准备
// ----------------------------
if (!fs.existsSync('tmp')) fs.mkdirSync('tmp')
if (!fs.existsSync('output')) fs.mkdirSync('output')

// ----------------------------
// 抓各区（每个区输出到一个目录）
// ----------------------------
for (const r of regions) {
  console.log('Fetching', r)

  // 清理旧目录
  const dir = `tmp/${r}`
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true })
  }

  execSync(
    `npx epg-grabber ` +
      `--config=epg_beinsports/beinsports.com.config.js ` +
      `--channels=epg_beinsports/${r}.channels.xml ` +
      `--output=${dir}`,
    { stdio: 'inherit' }
  )
}

// ----------------------------
// 正确 merge（合并目录，不是 XML）
// ----------------------------
console.log('Merging all regions...')

execSync(
  `npx epg-grabber merge ` +
    `--config=epg_beinsports/beinsports.com.config.js ` +
    `--output=output/epg_beinsports_raw.xml ` +
    `tmp/beinsports.com_*`,
  { stdio: 'inherit' }
)

console.log('✅ beIN 全区 EPG 抓取完成')

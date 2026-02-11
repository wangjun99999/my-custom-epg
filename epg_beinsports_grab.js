const { execSync } = require('child_process')
const fs = require('fs')

// --- 自动安装依赖 ---
try {
  require.resolve('axios')
} catch (e) {
  console.log('axios 不存在，正在安装...')
  execSync('npm install axios', { stdio: 'inherit' })
}

const regions = [
  'beinsports.com_mena-en',
  'beinsports.com_us-en',
  'beinsports.com_fr-fr',
  'beinsports.com_au-en',
  'beinsports.com_my-en',
  'beinsports.com_nz-en'
]

if (!fs.existsSync('tmp')) fs.mkdirSync('tmp')
if (!fs.existsSync('output')) fs.mkdirSync('output')

// 抓各区
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

// 正确合并
console.log('Merging XML...')
execSync(`npx epg-grabber merge "tmp/*.xml" > output/epg_beinsports_raw.xml`, {
  stdio: 'inherit'
})

const { execSync } = require('child_process')
const fs = require('fs')

function ensure(pkg) {
  try {
    require.resolve(pkg)
  } catch (e) {
    console.log(pkg, '不存在，正在安装...')
    execSync(`npm install ${pkg}`, { stdio: 'inherit' })
  }
}

// 这些是 beinsports.com.config.js 用到的
ensure('axios')
ensure('dayjs')

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

console.log('Merging XML...')
execSync(
  `npx epg-grabber merge ` +
  `--config=epg_beinsports/beinsports.com.config.js ` +
  `tmp/*.xml ` +
  `--output output/epg_beinsports_raw.xml`,
  { stdio: 'inherit' }
)


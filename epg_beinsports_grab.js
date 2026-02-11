const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

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

/* 1️⃣ 抓各区 EPG */
for (const r of regions) {
  console.log('Fetching', r)
  execSync(
    `npx epg-grabber --config=epg_beinsports/beinsports.com.config.js --channels=epg_beinsports/${r}.channels.xml --output=tmp/${r}.xml`,
    { stdio: 'inherit' }
  )
}

/* 2️⃣ 合并所有 xmltv */
console.log('Merging xml files...')

let programmes = []
let channels = new Map()

for (const file of fs.readdirSync('tmp')) {
  if (!file.endsWith('.xml')) continue

  const xml = fs.readFileSync(path.join('tmp', file), 'utf8')

  // channels
  for (const m of xml.matchAll(/<channel[\s\S]*?<\/channel>/g)) {
    const id = m[0].match(/id="([^"]+)"/)?.[1]
    if (id && !channels.has(id)) channels.set(id, m[0])
  }

  // programmes
  for (const m of xml.matchAll(/<programme[\s\S]*?<\/programme>/g)) {
    programmes.push(m[0])
  }
}

const out =
  `<?xml version="1.0" encoding="UTF-8"?>\n` +
  `<tv>\n` +
  [...channels.values()].join('\n') +
  '\n' +
  programmes.join('\n') +
  `\n</tv>\n`

fs.writeFileSync('output/epg_beinsports.xml', out, 'utf8')

console.log('Done: output/epg_beinsports.xml')

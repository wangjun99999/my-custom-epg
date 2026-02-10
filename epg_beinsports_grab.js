const { execSync } = require('child_process')
const fs = require('fs')

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
    `epg-grabber ` +
    `--config=epg_beinsports/beinsports.com.config.js ` +
    `--channels=epg_beinsports/${r}.channels.xml ` +
    `--output=tmp/${r}.xml`,
    { stdio: 'inherit' }
  )
}

execSync(`epg-grabber merge "tmp/*.xml" > output/epg_beinsports_raw.xml`, { stdio: 'inherit' })

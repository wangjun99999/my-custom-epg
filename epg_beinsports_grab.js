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
  execSync(`npx epg-grabber --site=beinsports.com --channels=epg_beinsports/${r}.channels.xml --output=tmp/${r}.xml`, { stdio: 'inherit' })
}

execSync(`npx epg-grabber merge "tmp/*.xml" > output/epg_beinsports_raw.xml`)

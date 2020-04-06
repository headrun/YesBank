#!/bin/sh

sudo apt install curl
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt install nodejs
npm i puppeteer
nmp i puppeteer-extra
npm i node-datetime
npm i puppeteer-extra-plugin-stealth
npm install express --save
npm install body-parser --save


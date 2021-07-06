#!/usr/bin/env bash

cd web
npm install
npm run build
cp -rf dist/ ../static/dist
#!/usr/bin/env node

// 设置环境变量来静默Sass警告
process.env.SASS_SILENCE_DEPRECATIONS = 'legacy-js-api,import';

// Node.js v25+ 兼容性补丁：fs.rmdirSync recursive 选项已移除
const fs = require('fs');
const path = require('path');
const os = require('os');
const patchFile = path.join(os.tmpdir(), 'fix-node-compat.js');
const patchContent = [
  'const fs = require("fs");',
  'const orig = fs.rmdirSync;',
  'fs.rmdirSync = function(p, o) {',
  '  if (o && o.recursive) {',
  '    try { fs.rmSync(p, Object.assign({}, o, {force:true})); } catch(e) {}',
  '    return;',
  '  }',
  '  return orig.call(fs, p, o);',
  '};',
].join('\n');
try { fs.writeFileSync(patchFile, patchContent); } catch(e) { /* ignore */ }

// 启动Vite开发服务器
const { spawn } = require('child_process');

const existingOpts = process.env.NODE_OPTIONS || '';
const vite = spawn('npx', ['vite', '--force'], {
  stdio: 'inherit',
  shell: true,
  env: {
    ...process.env,
    SASS_SILENCE_DEPRECATIONS: 'legacy-js-api,import',
    NODE_OPTIONS: `${existingOpts} --require ${patchFile}`.trim()
  }
});

vite.on('close', (code) => {
  process.exit(code);
});

vite.on('error', (err) => {
  console.error('启动失败:', err);
  process.exit(1);
});
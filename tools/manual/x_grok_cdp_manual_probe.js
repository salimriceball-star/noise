#!/usr/bin/env node
/*
Manual-only BrowserOS CDP helper for the noise idea-sourcing workflow.
This is not a scheduler or recurring automation. Use it only while an agent is
manually operating the fixed BrowserOS profile and inspecting X/Grok state.
*/
const fs = require('fs');
const http = require('http');
const WebSocket = require('ws');

function arg(name, fallback=null) {
  const idx = process.argv.indexOf(`--${name}`);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : fallback;
}

function flag(name) {
  return process.argv.includes(`--${name}`);
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    const req = http.get(url, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.setTimeout(10000, () => req.destroy(new Error('HTTP timeout')));
    req.on('error', reject);
  });
}

async function getTabs() {
  return await getJson('http://127.0.0.1:9100/json/list');
}

async function findTab(urlIncludes) {
  const tabs = await getTabs();
  const tab = tabs.find(t => t.type === 'page' && String(t.url || '').includes(urlIncludes));
  if (!tab) throw new Error(`No BrowserOS tab includes ${urlIncludes}`);
  return tab;
}

function withTab(tab, fn, timeoutMs=30000) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(tab.webSocketDebuggerUrl);
    let id = 0;
    const timer = setTimeout(() => {
      try { ws.close(); } catch (_) {}
      reject(new Error('CDP operation timed out'));
    }, timeoutMs);
    function send(method, params={}) {
      return new Promise((res, rej) => {
        const msgId = ++id;
        const handler = raw => {
          const msg = JSON.parse(raw);
          if (msg.id === msgId) {
            ws.off('message', handler);
            msg.error ? rej(msg.error) : res(msg.result);
          }
        };
        ws.on('message', handler);
        ws.send(JSON.stringify({id: msgId, method, params}));
      });
    }
    ws.on('open', async () => {
      try {
        await send('Page.enable');
        await send('Runtime.enable');
        await send('Page.bringToFront');
        const result = await fn(send);
        clearTimeout(timer);
        resolve(result);
      } catch (err) {
        clearTimeout(timer);
        reject(err);
      } finally {
        try { ws.close(); } catch (_) {}
      }
    });
    ws.on('error', err => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

async function captureHome(outPath) {
  const tab = await findTab('x.com/home');
  const payload = await withTab(tab, async send => {
    await send('Runtime.evaluate', {expression: 'window.scrollTo(0,0); true', returnByValue: true});
    await new Promise(r => setTimeout(r, 1000));
    const out = await send('Runtime.evaluate', {
      expression: `(() => ({
        captured_at: new Date().toISOString(),
        href: location.href,
        title: document.title,
        body: document.body.innerText,
        posts: [...document.querySelectorAll('article')].slice(0, 12).map((a, i) => ({i, text: a.innerText}))
      }))()`,
      returnByValue: true,
      awaitPromise: true
    });
    return out.result.value;
  });
  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2), 'utf8');
  console.log(outPath);
}

async function submitGrok(promptPath) {
  const prompt = fs.readFileSync(promptPath, 'utf8');
  const tab = await findTab('x.com/i/grok');
  const result = await withTab(tab, async send => {
    const out = await send('Runtime.evaluate', {
      expression: `(() => {
        const ta = document.querySelector('textarea[placeholder="무엇이든 물어보세요"]');
        if (!ta) return {ok:false, reason:'textarea missing'};
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, ${JSON.stringify(prompt)});
        ta.dispatchEvent(new InputEvent('input', {bubbles:true, data:${JSON.stringify(prompt)}, inputType:'insertText'}));
        ta.dispatchEvent(new Event('change', {bubbles:true}));
        const btn = [...document.querySelectorAll('button')].find(el => (el.getAttribute('aria-label') || '').includes('Grok'));
        if (!btn) return {ok:false, reason:'submit button missing'};
        const r = btn.getBoundingClientRect();
        return {ok:true, x:r.x + r.width/2, y:r.y + r.height/2, aria:btn.getAttribute('aria-label')};
      })()`,
      returnByValue: true,
      awaitPromise: true
    });
    const value = out.result.value;
    if (!value.ok) return value;
    await send('Input.dispatchMouseEvent', {type:'mouseMoved', x:value.x, y:value.y, button:'none'});
    await send('Input.dispatchMouseEvent', {type:'mousePressed', x:value.x, y:value.y, button:'left', clickCount:1});
    await send('Input.dispatchMouseEvent', {type:'mouseReleased', x:value.x, y:value.y, button:'left', clickCount:1});
    return value;
  });
  console.log(JSON.stringify(result, null, 2));
}

async function captureGrok(outPath) {
  const tab = await findTab('x.com/i/grok');
  const payload = await withTab(tab, async send => {
    const out = await send('Runtime.evaluate', {
      expression: `(() => ({
        captured_at: new Date().toISOString(),
        href: location.href,
        title: document.title,
        primary: (document.querySelector('[data-testid="primaryColumn"]') || document.body).innerText,
        body: document.body.innerText
      }))()`,
      returnByValue: true,
      awaitPromise: true
    });
    return out.result.value;
  });
  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2), 'utf8');
  console.log(outPath);
}

(async () => {
  const outPath = arg('out');
  if (flag('capture-home')) return await captureHome(outPath || 'x-home-capture.json');
  if (flag('submit-grok')) return await submitGrok(arg('prompt'));
  if (flag('capture-grok')) return await captureGrok(outPath || 'grok-capture.json');
  throw new Error('Usage: --capture-home --out path | --submit-grok --prompt file | --capture-grok --out path');
})().catch(err => {
  console.error(err);
  process.exit(1);
});

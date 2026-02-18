const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.setViewport({ width: 1024, height: 640 });

    const htmlPath = 'file://' + path.resolve('/Users/maxx/.openclaw/workspace/projects/smart-frame/index.html');
    await page.goto(htmlPath, { waitUntil: 'networkidle0' });

    // Inject data
    const weather = JSON.parse(fs.readFileSync('/Users/maxx/.openclaw/workspace/projects/smart-frame/weather.json', 'utf8'));
    const news = JSON.parse(fs.readFileSync('/Users/maxx/.openclaw/workspace/projects/smart-frame/news.json', 'utf8'));
    const moltbot = JSON.parse(fs.readFileSync('/Users/maxx/.openclaw/workspace/projects/smart-frame/moltbot.json', 'utf8'));
    const instagram = JSON.parse(fs.readFileSync('/Users/maxx/.openclaw/workspace/projects/smart-frame/instagram.json', 'utf8'));

    await page.evaluate((w, n, m, i) => {
        // Manually trigger the 'go' function logic with provided data
        const d = { maxx_status: { label: 'Maxx Moltbot', date: new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'short' }) } };
        
        const wd = w.weather;
        const ig = i.instagram;
        const news = n.news;
        const mb = m.moltbot;

        document.getElementById('w-loc').textContent = wd.location || 'Alajuela';
        document.getElementById('w-cond').textContent = wd.condition;
        document.getElementById('w-temp').textContent = wd.temp_c;
        document.getElementById('w-feels').textContent = wd.feels_like_c || wd.temp_c;
        document.getElementById('w-mm').textContent = '↑ ' + wd.max_temp_c + '° ↓ ' + wd.min_temp_c + '°';
        document.getElementById('w-wind').textContent = wd.wind_kmh + ' km/h';
        document.getElementById('w-hum').textContent = wd.humidity + '%';
        document.getElementById('w-uv').textContent = wd.uv_index;
        document.getElementById('w-prob').textContent = wd.prob_rain + '%';
        document.getElementById('w-icon').textContent = wd.icon;
        document.getElementById('w-updated').textContent = wd.last_updated;
        if (wd.bg_image) document.getElementById('w-bg').style.backgroundImage = "url('" + wd.bg_image + "')";
        if (wd.theme) document.getElementById('card-weather').setAttribute('data-theme', wd.theme);
        
        document.getElementById('ig-user').textContent = ig.username;
        document.getElementById('ig-foll').textContent = ig.followers;
        document.getElementById('ig-grow').textContent = ig.growth;
        document.getElementById('ig-posts').textContent = ig.posts;

        document.getElementById('m-label').textContent = 'Maxx Moltbot';
        document.getElementById('m-sub').textContent = mb.system.current_model + ' · ' + mb.state.logic_mode;
        document.getElementById('m-ctx-p').textContent = mb.system.context_usage;
        document.getElementById('m-ctx-bar').style.width = mb.system.context_usage;
        document.getElementById('m-tokens').textContent = '🧮 ' + mb.system.token_usage_daily + ' tokens';
        document.getElementById('m-date').textContent = d.maxx_status.date;
        document.getElementById('m-mood').textContent = mb.state.system_mood;
        document.getElementById('m-update').textContent = mb.operations.last_post_timestamp;

        const opsDiv = document.getElementById('m-ops');
        opsDiv.innerHTML = `
            <div class="m-pill"><div class="m-dot"></div>Goal: ${mb.operations.daily_goal_progress}</div>
            <div class="m-pill"><div class="m-dot"></div>ETA: ${mb.operations.next_post_eta}</div>
            <div class="m-pill" style="border-color:rgba(139, 92, 246, 0.3); color:rgba(139, 92, 246, 0.8)">${mb.state.last_action}</div>
        `;

        const nm = news.featured || {};
        document.getElementById('n-tag').textContent = nm.tag || 'AI News';
        document.getElementById('n-head').textContent = nm.headline || 'No headlines available';
        document.getElementById('n-source').textContent = nm.source || 'Unknown';
        if (nm.image_url) document.getElementById('n-card').style.backgroundImage = "url('" + nm.image_url + "')";

        const secCol = document.getElementById('n-sec-col');
        let secHtml = '';
        if (news.secondary_1) {
            secHtml += `<div class="n-sec-card"><div class="n-sec-head">${news.secondary_1.headline}</div><div class="n-sec-meta">${news.secondary_1.source}</div></div>`;
        }
        if (news.secondary_2) {
            secHtml += `<div class="n-sec-card"><div class="n-sec-head">${news.secondary_2.headline}</div><div class="n-sec-meta">${news.secondary_2.source}</div></div>`;
        }
        secCol.innerHTML = secHtml;
        
        // Final polish: frame id
        const now = new Date();
        const fid = now.getFullYear().toString().slice(-2) + 
                    (now.getMonth()+1).toString().padStart(2,'0') + 
                    now.getDate().toString().padStart(2,'0') + 
                    now.getHours().toString().padStart(2,'0') + 
                    now.getMinutes().toString().padStart(2,'0');
        document.getElementById('frame-id').textContent = 'FID: ' + fid;

    }, weather, news, moltbot, instagram);

    await page.screenshot({ path: '/Users/maxx/.openclaw/workspace/projects/smart-frame/Dashboard_Latest.png' });
    await browser.close();
})();

/* ═══════════════════════════════════════════════════════════════════════
   API Client — All fetch calls to the backend
   ═══════════════════════════════════════════════════════════════════════ */

const API_BASE = '/api';

const api = {
    async generate(prompt, language = 'python', maxLength = 256) {
        const res = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, language, max_length: maxLength }),
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async analyze(code, language = 'python') {
        const res = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, language }),
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async upload(file, language = 'auto') {
        const form = new FormData();
        form.append('file', file);
        form.append('language', language);
        const res = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: form,
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async autocomplete(code, language = 'python') {
        const res = await fetch(`${API_BASE}/autocomplete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, language }),
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async similarity(code1, code2, language = 'python') {
        const res = await fetch(`${API_BASE}/similarity`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code1, code2, language }),
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async languages() {
        const res = await fetch(`${API_BASE}/languages`);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
};

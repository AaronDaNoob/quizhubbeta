import { kv } from '@vercel/kv';
import { createHash } from 'node:crypto';

const DAY = 60 * 60 * 24;
const INITIAL_VISITS = 13900;
const VISITS_KEY = 'quiz-hub:visits';
const KV_TIMEOUT = 4000;

function withTimeout(promise) {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error('KV request timed out')), KV_TIMEOUT))
  ]);
}

function getClientKey(request) {
  const forwarded = request.headers.get('x-forwarded-for') || '';
  const ip = forwarded.split(',')[0].trim() || 'unknown';
  const userAgent = request.headers.get('user-agent') || 'unknown';
  return createHash('sha256').update(`${ip}:${userAgent}`).digest('hex');
}

function response(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store'
    }
  });
}

export default async function handler(request) {
  if (request.method !== 'GET' && request.method !== 'POST') {
    return response({ error: 'Method not allowed' }, 405);
  }

  try {
    await withTimeout(kv.set(VISITS_KEY, INITIAL_VISITS, { nx: true }));

    if (request.method === 'POST') {
      const visitorKey = `quiz-hub:visitor:${getClientKey(request)}`;
      const firstVisit = await withTimeout(kv.set(visitorKey, '1', { nx: true, ex: DAY }));
      if (firstVisit) await withTimeout(kv.incr(VISITS_KEY));
    }

    let visits = Number(await withTimeout(kv.get(VISITS_KEY)));
    if (!Number.isFinite(visits) || visits < INITIAL_VISITS) {
      await withTimeout(kv.set(VISITS_KEY, INITIAL_VISITS));
      visits = INITIAL_VISITS;
    }

    return response({ visits });
  } catch {
    return response({ visits: INITIAL_VISITS, fallback: true });
  }
}

import { kv } from '@vercel/kv';
import { createHash } from 'node:crypto';

const DAY = 60 * 60 * 24;
const INITIAL_VISITS = 13900;
const VISITS_KEY = 'quiz-hub:visits';

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
    await kv.set(VISITS_KEY, INITIAL_VISITS, { nx: true });

    if (request.method === 'POST') {
      const visitorKey = `quiz-hub:visitor:${getClientKey(request)}`;
      const firstVisit = await kv.set(visitorKey, '1', { nx: true, ex: DAY });
      if (firstVisit) await kv.incr(VISITS_KEY);
    }

    let visits = Number(await kv.get(VISITS_KEY));
    if (!Number.isFinite(visits) || visits < INITIAL_VISITS) {
      await kv.set(VISITS_KEY, INITIAL_VISITS);
      visits = INITIAL_VISITS;
    }

    return response({ visits });
  } catch {
    return response({ visits: INITIAL_VISITS, fallback: true });
  }
}

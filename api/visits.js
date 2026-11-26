import { kv } from '@vercel/kv';
import { createHash } from 'node:crypto';

const DAY = 60 * 60 * 24;

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
    if (request.method === 'POST') {
      const visitorKey = `quiz-hub:visitor:${getClientKey(request)}`;
      const firstVisit = await kv.set(visitorKey, '1', { nx: true, ex: DAY });
      if (firstVisit) await kv.incr('quiz-hub:visits');
    }

    const visits = Number(await kv.get('quiz-hub:visits')) || 0;
    return response({ visits });
  } catch {
    return response({ error: 'Visit counter unavailable' }, 503);
  }
}

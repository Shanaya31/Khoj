// Offline core: the city pack is cached on the device, and a mission can be built
// from it without any server. Anything that needs the network is an enhancement.

const KEY = (city) => `khoj:pack:${city}`;

export async function downloadPack(city) {
  const res = await fetch(`/api/city-pack/${city}`);
  if (!res.ok) throw new Error("Could not download the city pack.");
  const pack = await res.json();
  localStorage.setItem(KEY(city), JSON.stringify(pack));
  return pack;
}

export function loadPack(city) {
  try {
    const raw = localStorage.getItem(KEY(city));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function localMission(pack, { duration_minutes, interest }) {
  const pool = pack.missions.filter((m) => interest === "surprise" || m.interest === interest);
  const list = pool.length ? pool : pack.missions;
  const gap = (m) => Math.abs(m.duration_minutes - duration_minutes);
  const best = Math.min(...list.map(gap));
  const picks = list.filter((m) => gap(m) === best);
  const m = picks[Math.floor(Math.random() * picks.length)];
  return {
    session_id: `local-${Date.now()}`,
    city: pack.meta.city,
    duration_minutes,
    interest,
    source: "curated",
    mission: {
      title: m.title,
      intro: m.intro,
      objectives: m.objectives.map((text) => ({ text, fact_ids: [], place_id: null })),
      closing: "Put your phone away and start exploring.",
    },
  };
}

export function localJournal(session, observations, minutes) {
  const noted = observations.map((o) => o.text);
  return {
    title: session.mission.title,
    minutes,
    observation_count: noted.length,
    discoveries: noted.slice(0, 5),
    story: noted.length
      ? `You spent ${minutes} minutes exploring. Here is what caught your attention: ${noted.join("; ")}.`
      : `You spent ${minutes} minutes exploring with your phone mostly away. You didn't write anything down, and that counts too.`,
  };
}

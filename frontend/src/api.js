import { loadPack, localMission, localJournal } from "./offline.js";

async function post(path, body) {
  const res = await fetch(`/api${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function getCities() {
  const res = await fetch("/api/cities");
  if (!res.ok) throw new Error("Server unreachable");
  return res.json();
}

// Server first; if it is unreachable and a pack is cached, build the mission on-device.
export async function createMission(req) {
  try {
    return await post("/mission", req);
  } catch (err) {
    const pack = loadPack(req.city);
    if (!pack) throw err;
    return localMission(pack, req);
  }
}

export async function addObservation(session, obs) {
  if (session.session_id.startsWith("local-")) {
    return { ...obs, id: `o-${Date.now()}`, explanation: null };
  }
  try {
    return await post("/observation", { session_id: session.session_id, ...obs });
  } catch {
    return { ...obs, id: `o-${Date.now()}`, explanation: null, offline: true };
  }
}

export async function reflect(session, observations, minutes) {
  if (!session.session_id.startsWith("local-")) {
    try {
      return (await post("/reflection", { session_id: session.session_id })).journal;
    } catch {
      /* fall through to the on-device journal */
    }
  }
  return localJournal(session, observations, minutes);
}

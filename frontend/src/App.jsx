import { useEffect, useState } from "react";
import Setup from "./screens/Setup.jsx";
import Mission from "./screens/Mission.jsx";
import Explore from "./screens/Explore.jsx";
import Journal from "./screens/Journal.jsx";

const STATE_KEY = "khoj:active-session";

function restoreState() {
  try {
    const saved = localStorage.getItem(STATE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.session && ["mission", "explore", "journal"].includes(parsed.screen)) {
        return parsed;
      }
    }
  } catch {
    // Ignore invalid saved state and start fresh.
  }

  return { screen: "setup", session: null, journal: null };
}

export default function App() {
  const [initial] = useState(restoreState);
  const [screen, setScreen] = useState(initial.screen);
  const [session, setSession] = useState(initial.session);
  const [journal, setJournal] = useState(initial.journal);

  useEffect(() => {
    if (screen === "setup" || !session) {
      localStorage.removeItem(STATE_KEY);
      return;
    }

    try {
      localStorage.setItem(
        STATE_KEY,
        JSON.stringify({ screen, session, journal })
      );
    } catch {
      // Keep the app usable if local storage is unavailable.
    }
  }, [screen, session, journal]);

  const reset = () => {
    localStorage.removeItem(STATE_KEY);
    setSession(null);
    setJournal(null);
    setScreen("setup");
  };

  return (
    <main className="mx-auto min-h-screen max-w-xl px-5 py-8">
      {screen === "setup" && (
        <Setup
          onMission={(s) => {
            setSession(s);
            setJournal(null);
            setScreen("mission");
          }}
        />
      )}
      {screen === "mission" && (
        <Mission
          session={session}
          onStart={() => setScreen("explore")}
          onBack={reset}
        />
      )}
      {screen === "explore" && (
        <Explore
          session={session}
          onFinish={(j) => {
            setJournal(j);
            setScreen("journal");
          }}
        />
      )}
      {screen === "journal" && (
        <Journal journal={journal} onAgain={reset} />
      )}
    </main>
  );
}

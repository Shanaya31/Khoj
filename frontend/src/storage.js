const DB_NAME = "khoj-local";
const STORE_NAME = "observations";

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "key" });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function getStoredObservations(sessionId) {
  const db = await openDatabase();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readonly");
    const request = transaction.objectStore(STORE_NAME).getAll();

    request.onsuccess = () => {
      resolve(
        request.result
          .filter((item) => item.session_id === sessionId)
          .sort((a, b) => b.created_at - a.created_at)
          .map(({ key, session_id, ...observation }) => observation)
      );
    };

    request.onerror = () => reject(request.error);
    transaction.oncomplete = () => db.close();
  });
}

export async function saveStoredObservation(sessionId, observation) {
  const db = await openDatabase();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readwrite");
    transaction.objectStore(STORE_NAME).put({
      ...observation,
      key: `${sessionId}:${observation.id}`,
      session_id: sessionId,
      created_at: observation.created_at ?? Date.now(),
    });

    transaction.oncomplete = () => {
      db.close();
      resolve(observation);
    };

    transaction.onerror = () => {
      db.close();
      reject(transaction.error);
    };

    transaction.onabort = () => {
      db.close();
      reject(transaction.error || new Error("Local save was cancelled."));
    };
  });
}

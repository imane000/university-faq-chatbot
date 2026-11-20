const API_URL = (import.meta.env?.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

export const sendMessage = async (question) => {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    signal: AbortSignal.timeout(90000),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(
      typeof data?.detail === "string" ? data.detail : "La demande a échoué. Réessayez."
    );
  }
  if (typeof data?.response !== "string") {
    throw new Error("Réponse du serveur invalide.");
  }
  return data;
};

const API_BASE = import.meta.env.VITE_API_BASE || "";

export async function postScore(payload) {
  let resp;
  try {
    resp = await fetch(`${API_BASE}/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    throw new Error(
      "Could not reach the scoring server. Is the backend running on port 8000?"
    );
  }

  let body = null;
  try {
    body = await resp.json();
  } catch {
    body = null;
  }

  if (!resp.ok) {
    const fieldErrors = {};
    let message = "Request failed.";
    if (body && Array.isArray(body.errors)) {
      message = body.detail || "Validation failed.";
      for (const err of body.errors) {
        if (err.field) fieldErrors[err.field] = err.message;
      }
    } else if (body && body.detail) {
      message =
        typeof body.detail === "string" ? body.detail : "Request failed.";
    }
    const error = new Error(message);
    error.fieldErrors = fieldErrors;
    error.status = resp.status;
    throw error;
  }

  return body;
}

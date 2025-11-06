import { useCallback, useEffect, useState } from "react";

const API_BASE_URL = import.meta?.env?.VITE_API_BASE_URL ?? "http://localhost:8000";

async function fetchStats(modelId, userId) {
  const query = userId != null ? `?user_id=${userId}` : "";
  const response = await fetch(`${API_BASE_URL}/models/${modelId}/stats${query}`);
  if (!response.ok) {
    throw new Error("Failed to fetch stats");
  }
  return response.json();
}

async function sendAction(modelId, action, userId, extra = {}) {
  const response = await fetch(`${API_BASE_URL}/models/stats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, model_id: modelId, user_id: userId, ...extra }),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message = payload?.detail ?? "Failed to update stats";
    throw new Error(message);
  }
  return response.json();
}

export default function ModelDetail({ modelId, userId }) {
  const [downloads, setDownloads] = useState(0);
  const [favorites, setFavorites] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    fetchStats(modelId, userId)
      .then((stats) => {
        if (!mounted) return;
        setDownloads(stats.downloads);
        setFavorites(stats.favorites);
        if (typeof stats.is_favorite === "boolean") {
          setIsFavorite(stats.is_favorite);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message);
        }
      });
    return () => {
      mounted = false;
    };
  }, [modelId, userId]);

  const handleFavoriteToggle = useCallback(async () => {
    if (!userId) {
      setError("请先登录以收藏模型。");
      return;
    }
    setLoading(true);
    setError(null);
    const action = isFavorite ? "unfavorite" : "favorite";
    try {
      const stats = await sendAction(modelId, action, userId);
      setDownloads(stats.downloads);
      setFavorites(stats.favorites);
      if (typeof stats.is_favorite === "boolean") {
        setIsFavorite(stats.is_favorite);
      } else {
        setIsFavorite(action === "favorite");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isFavorite, modelId, userId]);

  return (
    <div className="model-detail">
      <div className="model-stats">
        <span className="model-stats__downloads">下载次数：{downloads}</span>
        <span className="model-stats__favorites">收藏人数：{favorites}</span>
      </div>
      <button className="model-favorite-btn" onClick={handleFavoriteToggle} disabled={loading}>
        {loading ? "处理中..." : isFavorite ? "取消收藏" : "收藏模型"}
      </button>
      {error ? <p className="model-error">{error}</p> : null}
    </div>
  );
}

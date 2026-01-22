import { useEffect, type ReactElement } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { setAuthToken } from "@shared/lib/auth";

export const AuthTokenHandler = (): ReactElement | null => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");
    if (!token) {
      return;
    }

    setAuthToken(token);
    params.delete("token");
    const nextSearch = params.toString();
    const nextPath = nextSearch ? `${location.pathname}?${nextSearch}` : location.pathname;
    navigate(nextPath, { replace: true });
  }, [location.pathname, location.search, navigate]);

  return null;
};

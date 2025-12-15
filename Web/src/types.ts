export interface Settings {
  refresh_interval_seconds: number;
  alert_interval_seconds: number;
  notification_enabled: boolean;
  send_key: string;
}

export interface PortfolioItem {
  code: string;
  name: string;
  held_shares: number;
  min_percentage: number;
  max_percentage: number;
}

export interface Config {
  settings: Settings;
  portfolio: PortfolioItem[];
}

export interface StatusResponse {
  message: string;
}
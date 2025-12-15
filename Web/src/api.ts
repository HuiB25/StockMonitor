import axios from 'axios';
import { Config, StatusResponse } from './types';

const api = axios.create({
  baseURL: '/', // Proxy handles the forwarding
});

export const getStatus = async (): Promise<StatusResponse> => {
  const response = await api.get<StatusResponse>('/status');
  return response.data;
};

export const getConfig = async (): Promise<Config> => {
  const response = await api.get<Config>('/config');
  return response.data;
};

export const updateConfig = async (config: Config): Promise<Config> => {
  const response = await api.post<Config>('/config', config);
  return response.data;
};
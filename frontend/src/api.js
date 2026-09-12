import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export async function askQuestion(question) {
  const response = await axios.post(`${API_BASE}/ask`, { question });
  return response.data;
}
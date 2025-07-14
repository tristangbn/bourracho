import axios from "axios";

const API_BASE = "http://localhost:8000/api/conversations/";

// List all conversations
export function fetchConversations() {
  return axios.get(`${API_BASE}all/`).then((res) => res.data.conversations);
}

// Create a new conversation
export function createConversation(metadata) {
  return axios.post(API_BASE, { metadata }).then((res) => res.data);
}

// Add user to conversation
export function addUser(conversationId, user) {
  return axios.post(`${API_BASE}${conversationId}/user/`, { user }).then((res) => res.data);
}

// Send a message
export function sendMessage(conversationId, message) {
  return axios.post(`${API_BASE}${conversationId}/message/`, { message }).then((res) => res.data);
}

// Get messages in a conversation
export function fetchMessages(conversationId) {
  return axios.get(`${API_BASE}${conversationId}/messages/get/`).then((res) => res.data.messages);
}

// Get users in a conversation
export function fetchUsers(conversationId) {
  return axios.get(`${API_BASE}${conversationId}/users/get/`).then((res) => res.data.users);
}

// Get metadata for a conversation
export function fetchMetadata(conversationId) {
  return axios.get(`${API_BASE}${conversationId}/metadata/get/`).then((res) => res.data.metadata);
}

import axios from "axios";

const DEFAULT_API_BASE = process.env.NODE_ENV === "production" ? "https://bourracho-production.up.railway.app/api/" : "http://localhost:8000/api/";
const API_BASE = process.env.REACT_APP_API_BASE || DEFAULT_API_BASE;

/**
 * List all conversations for a user
 * Backend: views.list_conversations (GET /api/conversations/all/<user_id>)
 * @param {string} userId
 */
export function fetchConversations(userId) {
  if (!userId) throw new Error("userId is required");
  return axios.get(`${API_BASE}conversations/${userId}/get`).then((res) => res.data.conversations);
}

/**
 * Create a new conversation
 * Backend: views.create_conversation (POST /api/conversations/add/)
 * Body: { metadata: {...} }
 */
// Create a new conversation for a user
export function createConversation(userId, metadata) {
  if (!userId) throw new Error("userId is required");
  return axios.post(`${API_BASE}conversations/${userId}/create`, { metadata }).then((res) => res.data);
}

/**
 * Add user to conversation
 * Backend: views.post_user (POST /api/conversations/<id>/user/)
 * Body: { user: {...} }
 */
// Join a user to a conversation
export function joinConversation(userId, conversationId) {
  if (!userId || !conversationId) throw new Error("userId and conversationId are required");
  return axios.post(`${API_BASE}conversations/${userId}/join`, { conversation_id: conversationId }).then((res) => res.data);
}

// Register a new user
export function registerUser(user) {
  return axios.post(`${API_BASE}auth/`, user).then((res) => res.data);
}

/**
 * Send a message
 * Backend: views.post_message (POST /api/conversations/<id>/message/)
 * Body: { message: {...} }
 */
/**
 * Send a message (with user_id)
 * Backend: views.post_message (POST /api/conversations/<id>/message/)
 * Body: { message: {...}, user_id: string }
 */
export function sendMessage(conversationId, message, userId) {
  if (!userId || !conversationId) throw new Error("userId and conversationId are required");
  return axios.post(`${API_BASE}messages/${userId}/${conversationId}`, { message }).then((res) => res.data);
}


/**
 * Get messages in a conversation
 * Backend: views.get_messages (GET /api/conversations/<id>/messages/get/)
 */
export function fetchMessages(userId, conversationId) {
  if (!userId || !conversationId) throw new Error("userId and conversationId are required");
  return axios.get(`${API_BASE}messages/${userId}/${conversationId}/get`).then((res) => res.data.messages);
}

/**
 * Get users in a conversation
 * Backend: views.get_users (GET /api/conversations/<id>/users/get/)
 */
export function fetchUsers(userId, conversationId) {
  if (!userId || !conversationId) throw new Error("userId and conversationId are required");
  return axios.get(`${API_BASE}users/${userId}/${conversationId}/get`).then((res) => res.data.users);
}

/**
 * Update metadata for a conversation (with user_id)
 * Backend: views.post_metadata (POST /api/conversations/<id>/metadata/)
 * Body: { metadata: {...}, user_id: string }
 */
export function updateMetadata(conversationId, metadata, userId) {
  if (!userId || !conversationId) throw new Error("userId and conversationId are required");
  return axios.post(`${API_BASE}metadata/${userId}/${conversationId}`, { metadata }).then((res) => res.data);
}

/**
 * Get metadata for a conversation
 * Backend: views.get_metadata (GET /api/conversations/<id>/metadata/get/)
 */
export function fetchMetadata(userId, conversationId) {
  if (!userId || !conversationId) throw new Error("userId and conversationId are required");
  return axios.get(`${API_BASE}metadata/${userId}/${conversationId}/get`).then((res) => res.data.metadata);
}

import React, { useState } from "react";
import { Box, Paper, Typography, TextField, Button, List, ListItem, ListItemText, CircularProgress } from "@mui/material";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { fetchMessages, sendMessage } from "../api/conversations";

function ChatWindow({ selectedConversationId, user }) {
  const [input, setInput] = useState("");
  const queryClient = useQueryClient();

  // Fetch messages for the selected conversation
  const { data: messages, isLoading, isError } = useQuery(
    ["messages", user?.id, selectedConversationId],
    () => fetchMessages(user.id, selectedConversationId),
    {
      enabled: !!selectedConversationId && !!user?.id,
    }
  );

  // Mutation for sending messages
  const mutation = useMutation(
    (msg) => sendMessage(selectedConversationId, msg, user.id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["messages", selectedConversationId]);
        setInput("");
      },
    }
  );

  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() && selectedConversationId && user) {
      mutation.mutate({
        author: user.name,
        content: input
      });
    }
  };

  return (
    <Paper sx={{ width: "100%", minHeight: 300, p: 2 }} elevation={3}>
      <Typography variant="h6" gutterBottom>
        Chat
      </Typography>
      {isLoading ? (
        <Box display="flex" justifyContent="center" my={2}>
          <CircularProgress size={32} />
        </Box>
      ) : isError ? (
        <Box color="error.main">Failed to load messages.</Box>
      ) : (
        <List sx={{ maxHeight: 200, overflow: "auto" }}>
          {messages && messages.length > 0 ? (
            messages.map((msg, idx) => (
              <ListItem key={msg.id || idx}>
                <ListItemText
                  primary={msg.content || msg.text}
                  secondary={msg.author || msg.user}
                />
              </ListItem>
            ))
          ) : (
            <ListItem>
              <ListItemText primary="No messages yet." />
            </ListItem>
          )}
        </List>
      )}
      <form onSubmit={handleSend} style={{ marginTop: 16, display: "flex", gap: 8 }}>
        <TextField
          variant="outlined"
          size="small"
          fullWidth
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <Button type="submit" variant="contained" color="primary">
          Send
        </Button>
      </form>
    </Paper>
  );
}

export default ChatWindow;

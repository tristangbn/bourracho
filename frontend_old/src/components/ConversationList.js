import React, { useState } from "react";
import { Box, Button, List, ListItem, ListItemText, Dialog, DialogTitle, DialogContent, TextField, CircularProgress } from "@mui/material";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { fetchConversations, createConversation, joinConversation } from "../api/conversations";

import { useSelector } from "react-redux";

function ConversationList({ onSelect, selectedConversationId }) {
  const user = useSelector((state) => state.user);

  const [open, setOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [selected, setSelected] = useState(null);
  const queryClient = useQueryClient();

  // Fetch conversations from API
  const {
    data: conversations = [],
    isLoading,
    isError,
  } = useQuery(
    ["conversations", user?.id],
    () => fetchConversations(user.id),
    { enabled: !!user?.id }
  );

  // Mutation for creating a conversation
  const mutation = useMutation(
    (metadata) => createConversation(user.id, metadata),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["conversations", user.id]);
        setOpen(false);
        setNewName("");
      },
    }
  );

  const handleCreate = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (newName) {
      mutation.mutate({ name: newName });
    }
  };

  return (
    <Box width="100%" mb={2}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <span>Conversations</span>
        <Button variant="outlined" size="small" onClick={handleCreate}>
          Create
        </Button>
      </Box>
      {isLoading ? (
        <Box display="flex" justifyContent="center" my={2}>
          <CircularProgress size={32} />
        </Box>
      ) : isError ? (
        <Box color="error.main">Failed to load conversations.</Box>
      ) : !user?.id ? (
        <Box color="text.secondary">Please log in to view your conversations.</Box>
      ) : conversations.length === 0 ? (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          p={3}
          sx={{ border: '1px dashed #ccc', borderRadius: 2, bgcolor: '#fafafa', minHeight: 120 }}
          mb={2}
        >
          <Box mb={1} fontWeight="bold" color="text.secondary">
            No conversations yet
          </Box>
          <Box mb={2} color="text.secondary">
            Create your first conversation or join one by ID below.
          </Box>
          <form
            onSubmit={e => {
              e.preventDefault();
              if (newName) mutation.mutate({ name: newName });
            }}
            style={{ width: '100%' }}
          >
            <TextField
              size="small"
              label="Conversation ID to Join"
              value={selected}
              onChange={e => setSelected(e.target.value)}
              sx={{ mb: 1, width: '100%' }}
            />
            <Button
              variant="outlined"
              color="primary"
              fullWidth
              disabled={!selected}
              onClick={async () => {
                if (selected && user?.id) {
                  await joinConversation(user.id, selected);
                  queryClient.invalidateQueries(["conversations", user.id]);
                  onSelect && onSelect(selected);
                }
              }}
              sx={{ mb: 1 }}
            >
              Join Conversation
            </Button>
          </form>
          <Button variant="contained" color="primary" onClick={handleCreate} sx={{ mt: 1 }}>
            Create Conversation
          </Button>
        </Box>
      ) : (
        <List>
          {conversations.map((conv) => (
            <ListItem
              button
              key={conv.conversation_id}
              selected={selectedConversationId === conv.conversation_id}
              onClick={() => onSelect && onSelect(conv.conversation_id)}
            >
              <ListItemText
                primary={conv.name || (conv.metadata && conv.metadata.name) || conv.conversation_id}
              />
            </ListItem>
          ))}
        </List>
      )}
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Create Conversation</DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <TextField
              autoFocus
              margin="dense"
              label="Conversation Name"
              fullWidth
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              required
            />
            <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
              Create
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </Box>
  );
}

export default ConversationList;

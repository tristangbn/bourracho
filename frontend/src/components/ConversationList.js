import React, { useState } from "react";
import { Box, Button, List, ListItem, ListItemText, Dialog, DialogTitle, DialogContent, TextField, CircularProgress } from "@mui/material";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { fetchConversations, createConversation } from "../api/conversations";

function ConversationList({ onSelect, selectedConversationId }) {
  const [open, setOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [selected, setSelected] = useState(null);
  const queryClient = useQueryClient();

  // Fetch conversations from API
  const { data: conversations, isLoading, isError } = useQuery(
    "conversations",
    fetchConversations
  );

  // Mutation for creating a conversation
  const mutation = useMutation(
    (metadata) => createConversation(metadata),
    {
      onSuccess: () => {
        queryClient.invalidateQueries("conversations");
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
      mutation.mutate({ title: newName });
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
                primary={conv.metadata && conv.metadata.title ? conv.metadata.title : conv.conversation_id}
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

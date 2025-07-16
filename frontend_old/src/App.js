import React from "react";
import { CssBaseline, Container, Box } from "@mui/material";
import UserAvatar from "./components/UserAvatar";
import ConversationList from "./components/ConversationList";
import ChatWindow from "./components/ChatWindow";

import { useState } from "react";
import { useSelector } from "react-redux";

function App() {
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const user = useSelector((state) => state.user);

  return (
    <>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box display="flex" flexDirection="column" alignItems="center" mt={2}>
          <UserAvatar />
          <ConversationList onSelect={setSelectedConversationId} selectedConversationId={selectedConversationId} />
          <ChatWindow selectedConversationId={selectedConversationId} user={user} />
        </Box>
      </Container>
    </>
  );
}

export default App;

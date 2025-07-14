import React, { useState } from "react";
import { Avatar, IconButton, Dialog, DialogTitle, DialogContent, TextField, Button, Box } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import { useDispatch, useSelector } from "react-redux";
import { setUser } from "../store/userSlice";

function UserAvatar() {
  const user = useSelector((state) => state.user);
  const dispatch = useDispatch();
  const [open, setOpen] = useState(!user.id);
  const [id, setId] = useState("");
  const [name, setName] = useState("");

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (id && name) {
      dispatch(setUser({ id, name }));
      setOpen(false);
    }
  };

  return (
    <Box display="flex" alignItems="center" mb={2}>
      <IconButton onClick={handleOpen}>
        <Avatar>{user.name ? user.name[0].toUpperCase() : <PersonIcon />}</Avatar>
      </IconButton>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Register / Login</DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <TextField
              autoFocus
              margin="dense"
              label="User ID"
              fullWidth
              value={id}
              onChange={(e) => setId(e.target.value)}
              required
            />
            <TextField
              margin="dense"
              label="Name"
              fullWidth
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
              Save
            </Button>
          </form>
        </DialogContent>
      </Dialog>
      <Box ml={1}>{user.name || "Guest"}</Box>
    </Box>
  );
}

export default UserAvatar;

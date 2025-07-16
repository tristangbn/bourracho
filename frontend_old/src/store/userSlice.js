import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  id: null,
  name: null,
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.id = action.payload.id;
      state.name = action.payload.name;
    },
    logout: (state) => {
      state.id = null;
      state.name = null;
    },
  },
});

export const { setUser, logout } = userSlice.actions;
export default userSlice.reducer;

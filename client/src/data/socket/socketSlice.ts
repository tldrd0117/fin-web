import { createSlice } from "@reduxjs/toolkit";

const socketSlice = createSlice({
    name: "socket",
    initialState: {
        isConnected: false
    },
    reducers:{
        connect: (state, action) => {
            state.isConnected = true
        },
        disconnect: (state, action) => {
            state.isConnected = false
        },
    }
})

const { actions, reducer } = socketSlice
export const { connect, disconnect } = actions
export default reducer
import { createAction, createSlice } from "@reduxjs/toolkit";

const socketSlice = createSlice({
    name: "socket",
    initialState: {
        isConnected: false,
        socket: undefined,
        isDestoried: false,
        socketConnection: undefined
    },
    reducers:{
        connect: (state, action) => {
            const { payload } = action
            state.isConnected = true
            state.socket = payload.socket
            state.socketConnection = payload.socketConnection
        },
        disconnect: (state, action) => {
            state.isConnected = false
        },
        destory: (state, action) => {
            state.isDestoried = true
        },
        create: (state, action) => {
            state.isDestoried = false
        }
    }
})

export const startConnection = createAction<any>("socket/startConnection");
export const endConnection = createAction<any>("socket/endConnection");

const { actions, reducer } = socketSlice
export const { connect, disconnect, destory, create } = actions
export default reducer
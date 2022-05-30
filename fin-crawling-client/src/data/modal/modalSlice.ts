import { createAction, createSlice } from "@reduxjs/toolkit";

const modalSlice = createSlice({
    name: "modal",
    initialState: {
        LoadingModal: true
    },
    reducers:{
        show: (state, action) => {
            const { payload } = action
            state[payload.modalName] = payload.isShow
        },
    }
})

const { actions, reducer } = modalSlice
export const { show } = actions
export default reducer
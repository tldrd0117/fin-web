import { createAction, createSlice } from "@reduxjs/toolkit";


const userSlice = createSlice({
    name: "user",
    initialState: {
        token: "TOKEN",
        username: "",
        errorMsg: ""
    },
    reducers:{
        fetchTokenSuccess: (state, action) => {
            const { payload } = action;
            state.token = payload.token;
        },
        fetchTokenFail: (state, action) => {
            const { payload } = action;
            state.errorMsg = payload.response.detail;
        }
    }
})

const { actions, reducer } = userSlice

export interface FetchTokenPayload{
    username: string
    password: string
}

export const fetchToken = createAction<FetchTokenPayload>("fetchToken");
export const { fetchTokenSuccess, fetchTokenFail } = actions
export default reducer
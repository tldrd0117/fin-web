import { createAction, createSlice } from "@reduxjs/toolkit";
import CryptoJs from 'crypto-js'
import JSEncrypt from "jsencrypt";


const userSlice = createSlice({
    name: "user",
    initialState: {
        token: "TOKEN",
        username: "",
        errorMsg: "",
        publicKey: ""
    },
    reducers:{
        fetchToken: (state, action) => {
            const { payload } = action;
            console.log(payload)
            const encrypt = new JSEncrypt({
                default_key_size: "2048",
                default_public_exponent: "010001",
                log: true
            });
            encrypt.setPublicKey(state.publicKey);
            payload.encPassword = encrypt.encrypt(payload.password);
            
        },
        fetchTokenSuccess: (state, action) => {
            const { payload } = action;
            state.token = payload.token;
        },
        fetchTokenFail: (state, action) => {
            const { payload } = action;
            state.errorMsg = payload.response.detail;
        },
        joinSuccess: (state, action) => {

        },
        joinFail: (state, action) => {
            const { payload } = action;
            state.errorMsg = payload.response.detail;

        },
        submitJoin: (state, action) => {
            const { payload } = action;
            const encrypt = new JSEncrypt();
            encrypt.setPublicKey(state.publicKey);
            payload.encPassword = encrypt.encrypt(payload.password);
            console.log(payload)
          
        },
        fetchPublicKeySuccess: (state, action) => {
            const { payload } = action;
            state.publicKey = payload.publicKey;
            console.log(payload)
        },
        fetchPublicKeyFail: (state, action) => {
            const { payload } = action;
            console.log(payload)
        }
    }
})

const { actions, reducer } = userSlice

export interface FetchTokenPayload{
    username: string
    password: string
}

export interface JoinPayLoad{
    username: string
    password: string
}

export const fetchPublicKey = createAction<{}>("fetchPublicKey");
export const { fetchToken, fetchTokenSuccess, fetchTokenFail, joinSuccess, joinFail, submitJoin, fetchPublicKeySuccess, fetchPublicKeyFail } = actions
export default reducer
import { configureStore, } from '@reduxjs/toolkit'
import rootReducer from "./data/root/rootReducer"

export default configureStore({
    reducer: rootReducer,
    devTools: true
})
import 'regenerator-runtime/runtime'
import { applyMiddleware, configureStore, } from '@reduxjs/toolkit'
import rootReducer from "./data/root/rootReducer"
import createSagaMiddleware from 'redux-saga'
import rootSaga from './data/segas'

const sagaMiddleware = createSagaMiddleware()

const store =  configureStore({
    reducer: rootReducer,
    devTools: true,
    middleware: [sagaMiddleware]
})

sagaMiddleware.run(rootSaga)

export default store

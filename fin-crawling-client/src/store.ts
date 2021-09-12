import 'regenerator-runtime/runtime'
import { applyMiddleware, configureStore, } from '@reduxjs/toolkit'
import rootReducer, {history} from "./data/root/rootReducer"
import createSagaMiddleware from 'redux-saga'
import rootSaga from './data/segas'
import { routerMiddleware } from 'connected-react-router'

const sagaMiddleware = createSagaMiddleware()

const store =  configureStore({
    reducer: rootReducer,
    devTools: true,
    middleware: [routerMiddleware(history), sagaMiddleware]
})

sagaMiddleware.run(rootSaga)

export default store

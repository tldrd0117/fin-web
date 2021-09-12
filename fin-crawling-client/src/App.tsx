import React from 'react';
import store from './store'
import Router from './Router'
import {Provider, useSelector} from 'react-redux'
import { ConnectedRouter } from 'connected-react-router';
import {history, RootState} from "./data/root/rootReducer"

export default () => {
    return <>
        <Provider store={store}>
            <Router/>
        </Provider>
    </>
}